# tracking/models.py
from .mongodb import livreurs_collection, positions_collection
import datetime
import uuid
from bson import ObjectId

def sanitize_mongo_doc(doc):
    """Retire le champ _id et convertit les ObjectId en string"""
    if doc and '_id' in doc:
        del doc['_id']
    return doc

class Livreur:
    @staticmethod
    def create(livreur_id, nom, telephone, actif=True):
        livreur = {
            "livreur_id": livreur_id,
            "nom": nom,
            "telephone": telephone,
            "actif": actif,
            "created_at": datetime.datetime.now()
        }
        result = livreurs_collection.insert_one(livreur)
        return sanitize_mongo_doc(livreur)
    
    @staticmethod
    def get_all():
        livreurs = list(livreurs_collection.find({}))
        return [sanitize_mongo_doc(doc) for doc in livreurs]
    
    @staticmethod
    def get_by_id(livreur_id):
        livreur = livreurs_collection.find_one({"livreur_id": livreur_id})
        return sanitize_mongo_doc(livreur) if livreur else None
    
    @staticmethod
    def update(livreur_id, data):
        livreurs_collection.update_one(
            {"livreur_id": livreur_id},
            {"$set": data}
        )
        return Livreur.get_by_id(livreur_id)

class Position:
    @staticmethod
    def create(livreur_id, latitude, longitude):
        position = {
            "position_id": str(uuid.uuid4()),
            "livreur_id": livreur_id,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "timestamp": datetime.datetime.now()
        }
        result = positions_collection.insert_one(position)
        return sanitize_mongo_doc(position)
    
    @staticmethod
    def get_latest_positions():
        # Agrégation pour obtenir la dernière position de chaque livreur
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {
                "_id": "$livreur_id",
                "position_id": {"$first": "$position_id"},
                "latitude": {"$first": "$latitude"},
                "longitude": {"$first": "$longitude"},
                "timestamp": {"$first": "$timestamp"}
            }},
            {"$project": {
                "_id": 0,
                "livreur_id": "$_id",
                "position_id": 1,
                "latitude": 1,
                "longitude": 1,
                "timestamp": 1
            }}
        ]
        return list(positions_collection.aggregate(pipeline))
    
    @staticmethod
    def get_livreur_positions(livreur_id, limit=100):
        positions = positions_collection.find(
            {"livreur_id": livreur_id}
        ).sort("timestamp", -1).limit(limit)
        return [sanitize_mongo_doc(doc) for doc in positions]