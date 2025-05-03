# salon/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AppointmentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("appointments", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("appointments", self.channel_name)

    async def appointment_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))



   
class CustomerQueryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("customer_queries", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("customer_queries", self.channel_name)

    async def customer_query_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))


    async def query_answered(self, event):
        await self.send(text_data=json.dumps({
            "type": event["event"],
            "data": event["data"],
        }))
