import requests
import time
import random
import math
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
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

# Créer les livreurs s'ils n'existent pas
def initialize_livreurs():
    for livreur in LIVREURS:
        try:
            response = requests.post(f"{BASE_URL}/livreurs/", json={
                "livreur_id": livreur["id"],
                "nom": livreur["nom"],
                "telephone": f"06{random.randint(10000000, 99999999)}",
                "actif": True
            })
            if response.status_code in [200, 201]:
                print(f"Livreur {livreur['nom']} créé ou existant")
        except Exception as e:
            print(f"Erreur lors de la création du livreur {livreur['nom']}: {e}")

# Générer un déplacement réaliste (trajectoire cohérente)
def simulate_movement(current_pos, base_center, max_distance=0.02):
    # Distance au centre de la zone
    dist_to_center = math.sqrt(
        (current_pos["lat"] - base_center["lat"])**2 + 
        (current_pos["lng"] - base_center["lng"])**2
    )
    
    # Si trop éloigné du centre, tendance à revenir
    if dist_to_center > max_distance:
        # Direction vers le centre avec un peu d'aléatoire
        vector_to_center = {
            "lat": base_center["lat"] - current_pos["lat"],
            "lng": base_center["lng"] - current_pos["lng"]
        }
        # Normaliser et ajouter un facteur aléatoire
        magnitude = math.sqrt(vector_to_center["lat"]**2 + vector_to_center["lng"]**2)
        move_lat = (vector_to_center["lat"] / magnitude) * 0.0008 + random.uniform(-0.0002, 0.0002)
        move_lng = (vector_to_center["lng"] / magnitude) * 0.0008 + random.uniform(-0.0002, 0.0002)
    else:
        # Mouvement plus aléatoire quand proche du centre
        move_lat = random.uniform(-0.0005, 0.0005)
        move_lng = random.uniform(-0.0005, 0.0005)
    
    # Mise à jour de la position
    current_pos["lat"] += move_lat
    current_pos["lng"] += move_lng
    
    return current_pos

def main():
    initialize_livreurs()
    
    print("Simulation de déplacement des livreurs...")
    print("Appuyez sur Ctrl+C pour arrêter.")
    
    # Positions actuelles des livreurs
    positions = {}
    for livreur in LIVREURS:
        # Position de départ dans la zone assignée
        zone = ZONES[livreur["zone"]]
        positions[livreur["id"]] = {
            "lat": zone["lat"] + random.uniform(-zone["radius"], zone["radius"]),
            "lng": zone["lng"] + random.uniform(-zone["radius"], zone["radius"])
        }
    
    # Compteurs pour statistiques
    iteration = 0
    successful_updates = 0
    failed_updates = 0
    
    try:
        while True:
            iteration += 1
            start_time = time.time()
            
            for livreur in LIVREURS:
                # Simuler un déplacement réaliste
                zone = ZONES[livreur["zone"]]
                positions[livreur["id"]] = simulate_movement(
                    positions[livreur["id"]], 
                    {"lat": zone["lat"], "lng": zone["lng"]},
                    zone["radius"] * 2
                )
                
                # Envoyer la nouvelle position
                try:
                    response = requests.post(f"{BASE_URL}/positions/", json={
                        "livreur": livreur["id"],
                        "latitude": positions[livreur["id"]]["lat"],
                        "longitude": positions[livreur["id"]]["lng"]
                    }, timeout=5)
                    
                    if response.status_code in [200, 201]:
                        print(f"{datetime.now().strftime('%H:%M:%S')} - Position mise à jour pour {livreur['nom']} "
                              f"({positions[livreur['id']]['lat']:.6f}, {positions[livreur['id']]['lng']:.6f})")
                        successful_updates += 1
                    else:
                        print(f"Erreur pour {livreur['nom']}: {response.status_code}")
                        failed_updates += 1
                except Exception as e:
                    print(f"Exception pour {livreur['nom']}: {e}")
                    failed_updates += 1
            
            # Calcul du temps d'attente pour maintenir la cadence
            elapsed = time.time() - start_time
            sleep_time = max(0, 5 - elapsed)  # 5 secondes entre chaque cycle
            
            # Afficher des statistiques toutes les 10 itérations
            if iteration % 10 == 0:
                print(f"\n--- Statistiques après {iteration} itérations ---")
                print(f"Mises à jour réussies: {successful_updates}")
                print(f"Mises à jour échouées: {failed_updates}")
                print(f"Taux de réussite: {successful_updates/(successful_updates+failed_updates or 1)*100:.1f}%\n")
            
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nSimulation terminée.")
        print(f"Nombre total d'itérations: {iteration}")
        print(f"Mises à jour réussies: {successful_updates}")
        print(f"Mises à jour échouées: {failed_updates}")

if __name__ == "__main__":
    main()