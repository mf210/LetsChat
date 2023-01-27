from collections import defaultdict

from django.contrib.auth import get_user_model
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .models import PrivateChatRoom, PrivateChatRoomMessage, UnreadPrivateChatMessages





User = get_user_model()
private_rooms_online_users = defaultdict(list)


class PrivateChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.roommate_name = self.scope["url_route"]["kwargs"]["roommate_name"]
        self.room_name = ''.join(sorted([self.user.username, self.roommate_name]))
        self.room_group_name = f"privatechat_{self.room_name}"
        if self.user.is_authenticated and await self.set_private_chat_room_obj():
            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            private_rooms_online_users[self.room_group_name].append(self.user.username)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        private_rooms_online_users[self.room_group_name].remove(self.user.username)

    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        command = content.get('command')
        message = content.get('message', '').strip()
        if command == 'send' and message:
            # save message
            pcrm_obj = await PrivateChatRoomMessage.objects.acreate(
                user=self.user,
                room=self.pcr_obj,
                content=message
            )
            await self.keep_track_unread_messages(pcrm_obj.content[:60])
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.user.username,
                    "profile_image_url": self.user.profile_image.url,
                    "profile_url": self.user.get_absolute_url(),
                    "msg_timestamp": pcrm_obj.timestamp.ctime(),
                    "msg_id": pcrm_obj.id,
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    
    ################### Database Queries ###################
    @database_sync_to_async
    def set_private_chat_room_obj(self):
        # set PrivateChatRoom object and return true if these two users are friends with each other
        try:
            self.roommate = User.objects.get(username=self.roommate_name)
            if self.user.friendship.is_friend_with(self.roommate):
                self.pcr_obj, _ = PrivateChatRoom.objects.get_or_create(name=self.room_name)
                return True
        except (User.DoesNotExist, PrivateChatRoom.DoesNotExist):
            pass
        return False
    
    async def keep_track_unread_messages(self, msg):
        """
        Increment the number of roommate unread messages if he/she is not in this chat-room
        """
        if self.roommate_name not in private_rooms_online_users[self.room_group_name]:
            upcm_obj, created = await UnreadPrivateChatMessages.objects.aget_or_create(
                user=self.roommate,
                room=self.pcr_obj,
                defaults={'sender': self.user, 'most_recent_message': msg}
            )
            if not created:
                upcm_obj.count += 1
                upcm_obj.most_recent_message = msg
                await database_sync_to_async(upcm_obj.save)(
                    update_fields=['count', 'most_recent_message', 'timestamp']
                )
            await self.channel_layer.group_send(
                f'notification_{self.roommate_name}',
                {
                    'type': 'general_notification',
                    'command': 'append_new_chat_notification',
                    'notification': {
                        'id': upcm_obj.id,
                        'count': upcm_obj.count,
                        'most_recent_message': msg,
                        'most_recent_message_timestamp': upcm_obj.timestamp.isoformat(),
                        'sender_username': self.user.username,
                        'sender_profile_image': self.user.profile_image.url,
                    }
                }
            )