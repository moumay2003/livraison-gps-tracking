# tracking/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from bson import ObjectId

# Classe pour encoder les types MongoDB en JSON
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class TrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "tracking_updates",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "tracking_updates",
            self.channel_name
        )

    async def position_update(self, event):
        # Envoie la mise à jour au client
        await self.send(text_data=json.dumps({
            'livreur_id': event['livreur_id'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'timestamp': event['timestamp'],
        }, cls=MongoJSONEncoder))