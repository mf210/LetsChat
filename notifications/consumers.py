from collections import defaultdict

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from privatechats.models import UnreadPrivateChatMessages



MAX_CONN_FOR_USER = 3
online_users = defaultdict(list)


class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_group_name = f"notification_{self.user.username}"
        if self.user.is_authenticated:
            self.friends = await self.friends_list()
            # Join room group and keep track of online users
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            online_users[self.user.username].append(self)
            if len(online_users[self.user.username]) == 1:
                # Send to the user's friends that this user is online
                async for friend in self.friends:
                    for conn in online_users[friend.username]:
                        await conn.send_friends_status()
            # close this user's oldest websocket connection
            if len(online_users[self.user.username]) > MAX_CONN_FOR_USER:
                await online_users[self.user.username][0].close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        online_users[self.user.username].remove(self)
        if len(online_users[self.user.username]) == 0:
            # Send to the user's friends that this user is offline
            async for friend in self.friends:
                    for conn in online_users[friend.username]:
                        await conn.send_friends_status()


    # Receive message from WebSocket
    async def receive_json(self, content, **kwargs):
        command = content.get('command')
        if command == 'get_unread_general_notifications_count':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "general_notification",
                    "command": "set_unread_general_notifications_count",
                    "count": await self.user.notifications.filter(is_read=False).acount(),
                }
            )
        elif command == 'mark_notifications_read':
            await self.user.notifications.filter(is_read=False).aupdate(is_read=True)
        elif command == 'mark_chat_notification_read':
            upcm_id = content.get('id')
            try:
                await self.user.unread_private_messages.filter(id=upcm_id).aupdate(count=0)
            except (UnreadPrivateChatMessages.DoesNotExist, ValueError):
                pass

    async def send_friends_status(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'general_notification',
                'command': 'update_friends_status',
                'friends_status': { 
                    friend.username: 'online' if len(online_users[friend.username]) >= 1 else 'offline'
                    async for friend in self.friends
                }
            }
        )

    # Receive message from room group
    async def general_notification(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    @database_sync_to_async
    def friends_list(self):
        return self.user.friendship.friends.all()
        