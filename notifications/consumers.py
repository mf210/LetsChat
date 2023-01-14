from channels.generic.websocket import AsyncJsonWebsocketConsumer





class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.room_group_name = f"notification_{self.user.username}"
        if self.user.is_authenticated:
            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

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

    # Receive message from room group
    async def general_notification(self, event):
        # Send message to WebSocket
        await self.send_json(event)