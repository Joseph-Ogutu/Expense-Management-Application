import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class ExpenseConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_discard("expenses", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("expenses", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            "expenses",
            {
                "type": "expense_update",
                "data": data,
            },
        )

    async def expenses_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

