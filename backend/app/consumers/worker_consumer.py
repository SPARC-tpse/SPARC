import json

from channels.generic.websocket import AsyncWebsocketConsumer


class WorkerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "workers"
        self.room_group_name = f"workers_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        print(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"WebSocket disconnected: {self.channel_name}")

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            print(f"Received: {data}")

    # Receive message from room group
    async def worker_message(self, event):
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": event["type"],
                    "action": event["action"],
                    "data": event.get("data", {}),
                }
            )
        )
