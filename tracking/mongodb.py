from pymongo import MongoClient
from django.conf import settings
import datetime

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['livreurs_gps_db']  # Nom de votre base de données

# Collections
livreurs_collection = db['livreurs']
positions_collection = db['positions']

# Création des index nécessaires
positions_collection.create_index([("livreur_id", 1), ("timestamp", -1)])