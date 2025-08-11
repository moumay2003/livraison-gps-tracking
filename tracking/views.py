# tracking/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Livreur, Position
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from bson import ObjectId
from datetime import datetime

# Classe pour encoder les types MongoDB en JSON
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Fonction helper pour renvoyer des réponses JSON
def mongo_json_response(data, **kwargs):
    return JsonResponse(
        json.loads(json.dumps(data, cls=MongoJSONEncoder)),
        **kwargs
    )

@csrf_exempt
@require_http_methods(["GET", "POST"])
def livreurs_view(request):
    if request.method == "GET":
        livreurs = Livreur.get_all()
        return mongo_json_response(livreurs, safe=False)
    
    elif request.method == "POST":
        data = json.loads(request.body)
        livreur = Livreur.create(
            data.get('livreur_id'),
            data.get('nom'),
            data.get('telephone'),
            data.get('actif', True)
        )
        return mongo_json_response(livreur, safe=False)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def livreur_detail_view(request, livreur_id):
    if request.method == "GET":
        livreur = Livreur.get_by_id(livreur_id)
        if livreur:
            return mongo_json_response(livreur, safe=False)
        return JsonResponse({"error": "Livreur non trouvé"}, status=404)
    
    elif request.method == "PUT":
        data = json.loads(request.body)
        livreur = Livreur.update(livreur_id, data)
        return mongo_json_response(livreur, safe=False)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def positions_view(request):
    if request.method == "GET":
        if request.GET.get('latest') == 'true':
            positions = Position.get_latest_positions()
        else:
            positions = []
        return mongo_json_response(positions, safe=False)
    
    elif request.method == "POST":
        data = json.loads(request.body)
        position = Position.create(
            data.get('livreur'),
            data.get('latitude'),
            data.get('longitude')
        )
        
        # Notifier via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "tracking_updates",
            {
                "type": "position_update",
                "livreur_id": position["livreur_id"],
                "latitude": position["latitude"],
                "longitude": position["longitude"],
                "timestamp": position["timestamp"].isoformat(),
            }
        )
        
        return mongo_json_response(position, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def livreur_positions_view(request, livreur_id):
    positions = Position.get_livreur_positions(livreur_id)
    return mongo_json_response(positions, safe=False)