import requests
import time
import random
import logging
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class DeliverySimulator:
    # Configuration par défaut
    DEFAULT_BASE_URL = "http://localhost:8000/api"
    DEFAULT_UPDATE_INTERVAL = 10  # secondes - modifié à 10 secondes
    
    # Liste des livreurs
    LIVREURS = [
        {"id": "LIV001", "nom": "Jean Dupont", "zone": "Nord Paris"},
        {"id": "LIV002", "nom": "Marie Martin", "zone": "Sud Paris"},
        {"id": "LIV003", "nom": "Pierre Durand", "zone": "Est Paris"},
        {"id": "LIV004", "nom": "Sophie Lefebvre", "zone": "Ouest Paris"},
        {"id": "LIV005", "nom": "Lucas Moreau", "zone": "Centre Paris"}
    ]
    
    # Points de départ dans différentes zones de Paris
    ZONES = {
        "Nord Paris": {"lat": 48.882, "lng": 2.350, "radius": 0.01},
        "Sud Paris": {"lat": 48.830, "lng": 2.355, "radius": 0.01},
        "Est Paris": {"lat": 48.855, "lng": 2.390, "radius": 0.01},
        "Ouest Paris": {"lat": 48.856, "lng": 2.310, "radius": 0.01},
        "Centre Paris": {"lat": 48.856, "lng": 2.352, "radius": 0.008}
    }
    
    def __init__(self, base_url=None, update_interval=None):
        """Initialise le simulateur avec les paramètres fournis ou par défaut."""
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.update_interval = update_interval or self.DEFAULT_UPDATE_INTERVAL
        self.positions = {}
        self.previous_positions = {}  # Pour suivre les positions précédentes
        self.stats = {
            "iterations": 0,
            "successful_updates": 0,
            "failed_updates": 0
        }
        self._initialize_positions()
        self.session = requests.Session()  # Utilisation d'une session pour optimiser les connexions
    
    def _initialize_positions(self) -> None:
        """Initialise les positions de départ des livreurs."""
        for livreur in self.LIVREURS:
            zone = self.ZONES[livreur["zone"]]
            self.positions[livreur["id"]] = {
                "lat": zone["lat"] + random.uniform(-zone["radius"], zone["radius"]),
                "lng": zone["lng"] + random.uniform(-zone["radius"], zone["radius"])
            }
            self.previous_positions[livreur["id"]] = self.positions[livreur["id"]].copy()
    
    def initialize_livreurs(self) -> None:
        """Crée les livreurs s'ils n'existent pas déjà."""
        logger.info("Initialisation des livreurs...")
        
        for livreur in self.LIVREURS:
            try:
                response = self.session.post(
                    f"{self.base_url}/livreurs/", 
                    json={
                        "livreur_id": livreur["id"],
                        "nom": livreur["nom"],
                        "telephone": f"06{random.randint(10000000, 99999999)}",
                        "actif": True
                    },
                    timeout=5
                )
                if response.status_code in [200, 201]:
                    logger.info(f"Livreur {livreur['nom']} créé ou existant")
                else:
                    logger.warning(f"Erreur {response.status_code} pour {livreur['nom']}")
            except Exception as e:
                logger.error(f"Erreur lors de la création du livreur {livreur['nom']}: {e}")
    
    def generate_random_position(self, livreur_id: str) -> Dict[str, float]:
        """Génère une position totalement aléatoire dans la zone du livreur."""
        livreur = next((l for l in self.LIVREURS if l["id"] == livreur_id), None)
        if not livreur:
            return self.positions[livreur_id]
            
        zone = self.ZONES[livreur["zone"]]
        return {
            "lat": zone["lat"] + random.uniform(-zone["radius"], zone["radius"]),
            "lng": zone["lng"] + random.uniform(-zone["radius"], zone["radius"])
        }
    
    def update_position(self, livreur: Dict[str, str]) -> None:
        """Met à jour la position d'un livreur et l'envoie au serveur."""
        try:
            # Sauvegarder la position actuelle
            self.previous_positions[livreur["id"]] = self.positions[livreur["id"]].copy()
            
            # Générer une nouvelle position complètement aléatoire
            self.positions[livreur["id"]] = self.generate_random_position(livreur["id"])
            
            # Envoyer la nouvelle position
            response = self.session.post(
                f"{self.base_url}/positions/", 
                json={
                    "livreur": livreur["id"],
                    "latitude": self.positions[livreur["id"]]["lat"],
                    "longitude": self.positions[livreur["id"]]["lng"],
                    "timestamp": datetime.now().isoformat()
                },
                timeout=5
            )
            
            current_pos = self.positions[livreur["id"]]
            prev_pos = self.previous_positions[livreur["id"]]
            
            # Calculer la distance parcourue
            distance = self.calculate_distance(prev_pos, current_pos)
            
            if response.status_code in [200, 201]:
                # Affichage visuel du déplacement
                self.display_movement(livreur, prev_pos, current_pos, distance)
                self.stats["successful_updates"] += 1
            else:
                logger.warning(f"Erreur {response.status_code} pour {livreur['nom']}: {response.text}")
                self.stats["failed_updates"] += 1
        except Exception as e:
            logger.error(f"Exception pour {livreur['nom']}: {str(e)}")
            self.stats["failed_updates"] += 1
    
    def calculate_distance(self, pos1: Dict[str, float], pos2: Dict[str, float]) -> float:
        """Calcule la distance approximative entre deux positions en mètres."""
        # Conversion en radians
        lat1, lon1 = pos1["lat"] * (3.14159/180), pos1["lng"] * (3.14159/180)
        lat2, lon2 = pos2["lat"] * (3.14159/180), pos2["lng"] * (3.14159/180)
        
        # Rayon de la Terre en mètres
        R = 6371000
        
        # Formule haversine
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (pow(pow(dlat, 2), 0.5)) + pow(pow(dlon * pow(dlon, 2), 0.5), 0.5)
        c = 2 * pow(pow(a/2, 2), 0.5)
        distance = R * c
        
        return distance
    
    def display_movement(self, livreur: Dict[str, str], prev_pos: Dict[str, float], 
                        current_pos: Dict[str, float], distance: float) -> None:
        """Affiche le déplacement d'un livreur de façon visuelle."""
        # Caractères pour représenter les directions
        direction = ""
        if current_pos["lat"] > prev_pos["lat"]:
            direction += "↑ N "  # Nord
        elif current_pos["lat"] < prev_pos["lat"]:
            direction += "↓ S "  # Sud
            
        if current_pos["lng"] > prev_pos["lng"]:
            direction += "→ E"  # Est
        elif current_pos["lng"] < prev_pos["lng"]:
            direction += "← O"  # Ouest
            
        # Formatage des coordonnées
        logger.info(f"\n[DÉPLACEMENT] {livreur['nom']} ({livreur['zone']})")
        logger.info(f"  De: ({prev_pos['lat']:.6f}, {prev_pos['lng']:.6f})")
        logger.info(f"  À:  ({current_pos['lat']:.6f}, {current_pos['lng']:.6f})")
        logger.info(f"  Direction: {direction}")
        logger.info(f"  Distance: {distance:.2f} mètres")
        
        # Enregistrer le déplacement dans un fichier JSON
        self.save_movement_to_file(livreur, prev_pos, current_pos, distance)
    
    def save_movement_to_file(self, livreur: Dict[str, str], prev_pos: Dict[str, float],
                             current_pos: Dict[str, float], distance: float) -> None:
        """Enregistre les déplacements dans un fichier JSON pour visualisation ultérieure."""
        try:
            movement_data = {
                "timestamp": datetime.now().isoformat(),
                "livreur_id": livreur["id"],
                "livreur_nom": livreur["nom"],
                "zone": livreur["zone"],
                "previous_position": prev_pos,
                "current_position": current_pos,
                "distance": distance
            }
            
            # Nom du fichier basé sur la date
            filename = f"mouvements_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Charger le fichier existant ou créer une nouvelle liste
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []
            
            # Ajouter le nouveau mouvement
            data.append(movement_data)
            
            # Sauvegarder le fichier
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du mouvement: {e}")
    
    def display_stats(self) -> None:
        """Affiche les statistiques de la simulation."""
        total_attempts = self.stats["successful_updates"] + self.stats["failed_updates"]
        success_rate = (self.stats["successful_updates"] / total_attempts) * 100 if total_attempts > 0 else 0
        
        logger.info("\n--- Statistiques de simulation ---")
        logger.info(f"Nombre d'itérations: {self.stats['iterations']}")
        logger.info(f"Mises à jour réussies: {self.stats['successful_updates']}")
        logger.info(f"Mises à jour échouées: {self.stats['failed_updates']}")
        logger.info(f"Taux de réussite: {success_rate:.1f}%")
        logger.info("-----------------------------\n")
    
    def run(self) -> None:
        """Lance la simulation de déplacement des livreurs."""
        self.initialize_livreurs()
        
        logger.info("Simulation de déplacement des livreurs...")
        logger.info(f"Intervalle entre mises à jour: {self.update_interval} secondes")
        logger.info("Appuyez sur Ctrl+C pour arrêter.")
        
        try:
            while True:
                self.stats["iterations"] += 1
                start_time = time.time()
                
                logger.info(f"\n=== CYCLE DE MISE À JOUR #{self.stats['iterations']} ===")
                
                # Mise à jour séquentielle pour une meilleure lisibilité des logs
                for livreur in self.LIVREURS:
                    self.update_position(livreur)
                    time.sleep(0.5)  # Petit délai entre chaque livreur pour mieux visualiser
                
                # Afficher des statistiques à chaque itération
                self.display_stats()
                
                # Calcul du temps d'attente pour maintenir la cadence
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                
                if sleep_time > 0:
                    logger.info(f"Attente de {sleep_time:.1f} secondes avant le prochain cycle...")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logger.info("\nSimulation terminée.")
            self.display_stats()
            logger.info(f"Les données de mouvement ont été enregistrées dans le fichier mouvements_{datetime.now().strftime('%Y%m%d')}.json")
    
    @staticmethod
    def add_command_line_args():
        """Configure et analyse les arguments de la ligne de commande."""
        parser = argparse.ArgumentParser(description="Simulateur de déplacement GPS de livreurs")
        parser.add_argument("--url", dest="base_url", default=DeliverySimulator.DEFAULT_BASE_URL,
                            help=f"URL de base de l'API (défaut: {DeliverySimulator.DEFAULT_BASE_URL})")
        parser.add_argument("--interval", dest="update_interval", type=float, 
                            default=DeliverySimulator.DEFAULT_UPDATE_INTERVAL,
                            help=f"Intervalle entre les mises à jour en secondes (défaut: {DeliverySimulator.DEFAULT_UPDATE_INTERVAL})")
        parser.add_argument("--debug", action="store_true", help="Active le mode debug avec plus de logs")
        return parser.parse_args()

def main():
    # Traitement des arguments de ligne de commande
    args = DeliverySimulator.add_command_line_args()
    
    # Configuration du niveau de log selon le mode debug
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Mode debug activé")
    
    # Création et exécution du simulateur
    simulator = DeliverySimulator(base_url=args.base_url, update_interval=args.update_interval)
    simulator.run()

if __name__ == "__main__":
    main()