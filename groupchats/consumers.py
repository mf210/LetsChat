from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .models import GroupChatRoom, GroupChatRoomMessage




class GroupChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"groupchat_{self.room_name}"
        if self.user.is_authenticated \
           and await self.set_group_chat_room_obj() \
           and await self.is_user_in_gcr_users_list():
            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        command = content.get('command')
        message = content.get('message', '').strip()
        if command == 'send' and message:
            gcrm_obj = await self.save_message(message)
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.user.username,
                    "profile_image_url": self.user.profile_image.url,
                    "profile_url": self.user.get_absolute_url(),
                }
            )
    
    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send_json({
            'message': event["message"],
            'username': event["username"],
            'profile_image_url': event["profile_image_url"],
            "profile_url": event["profile_url"],
        })

    
    ############### Database Queries ###############
    @database_sync_to_async
    def set_group_chat_room_obj(self):
        # set group room object and return true if it's exisit
        try:
            self.gcr_obj = GroupChatRoom.objects.get(name=self.room_name)
            return True
        except GroupChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def is_user_in_gcr_users_list(self):
        return self.gcr_obj.users.filter(pk=self.user.pk).exists()

    @database_sync_to_async
    def save_message(self, msg):
        # save and return GroupChatRoomMessage object
        return GroupChatRoomMessage.objects.create(
            user=self.user,
            room=self.gcr_obj,
            content=msg
        )