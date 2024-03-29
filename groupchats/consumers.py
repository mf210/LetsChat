from collections import defaultdict

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .models import GroupChatRoom, GroupChatRoomMessage



MAX_CONN_PER_ROOM = 2
group_rooms_online_users = defaultdict(lambda: defaultdict(list))


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
            user_conns = group_rooms_online_users[self.room_group_name][self.user.username]
            user_conns.append(self)
            if len(user_conns) == 1:
                # send count of online users in room if the user connected for first time 
                await self.send_room_online_users_count_for_group()
            if len(user_conns) > MAX_CONN_PER_ROOM:
                # close the user's oldest websocket connection
                await user_conns[0].close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        user_conns = group_rooms_online_users[self.room_group_name][self.user.username]
        user_conns.remove(self)
        if len(user_conns) == 0:
            # update and send count of online users in room if the user has no connection
            del group_rooms_online_users[self.room_group_name][self.user.username]
            await self.send_room_online_users_count_for_group()

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
                    "msg_timestamp": gcrm_obj.timestamp.isoformat(),
                    "msg_id": gcrm_obj.id,
                }
            )
    
    async def send_room_online_users_count_for_group(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_online_users_count',
                'room_online_users_count': len(group_rooms_online_users[self.room_group_name]),
            }
        )
    
    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send_json(event)
    
    async def room_online_users_count(self, event):
        # Send count of online users in this room group to WebSocket
        await self.send_json(event)
    
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