import psutil
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import urllib.parse

# --- CONFIGURATION INITIALE ---
# Initialisation des compteurs au lancement du script pour le calcul du débit réseau
last_net_stats = psutil.net_io_counters()
last_time = time.time()

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global last_net_stats, last_time
        
        # --- GESTION DE L'OUVERTURE DE L'EXPLORATEUR ---
        if self.path.startswith('/open'):
            try:
                # Récupère le chemin après ?path=
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                path_to_open = params.get('path', [None])[0]
                
                if path_to_open:
                    os.startfile(path_to_open)
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b"OK")
                    return
            except Exception as e:
                print(f"Erreur lors de l'ouverture du dossier : {e}")
                self.send_response(500)
                self.end_headers()
                return

        # --- GESTION DES STATISTIQUES (Code original) ---
        # Gestion du temps pour un calcul de débit précis
        current_time = time.time()
        interval = current_time - last_time
        
        # Empêche les erreurs de division par zéro
        if interval <= 0.1: interval = 0.1

        # --- SECTION RÉSEAU (Download / Upload) ---
        current_net = psutil.net_io_counters()
        
        # Calcul du débit (Octets par seconde)
        bytes_in = (current_net.bytes_recv - last_net_stats.bytes_recv) / interval
        bytes_out = (current_net.bytes_sent - last_net_stats.bytes_sent) / interval
        
        # --- SECTION PERFORMANCE (CPU & RAM) ---
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent

        # --- PARTIE DISQUES (Calcul en Go + Pourcentage) ---
        def get_disk_info(path):
            try:
                usage = psutil.disk_usage(path)
                return {
                    "percent": usage.percent,
                    "used": round(usage.used / (1024**3), 1),
                    "total": round(usage.total / (1024**3), 0)
                }
            except Exception:
                return {"percent": 0, "used": 0, "total": 0}

        # --- PRÉPARATION DES DONNÉES JSON ---
        data = {
            "net": {
                "in": round(bytes_in / 1024, 2),
                "out": round(bytes_out / 1024, 2)
            },
            "performance": {
                "cpu": cpu_usage,
                "ram": ram_usage
            },
            "disks": {
                "c": get_disk_info('C:'),
                "e": get_disk_info('E:'),
                "f": get_disk_info('F:')
            }
        }

        # Mise à jour des compteurs pour la prochaine requête
        last_net_stats = current_net
        last_time = current_time

        # --- RÉPONSE HTTP ---
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') 
            self.end_headers()
            
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except Exception as e:
            print(f"Erreur d'envoi HTTP : {e}")

    def log_message(self, format, *args):
        return 

# --- DÉMARRAGE DU SERVEUR ---
if __name__ == "__main__":
    PORT = 9999
    try:
        server = HTTPServer(('localhost', PORT), DashboardHandler)
        print(f">>> PONT SYSTÈME ROG [PERF + DISQUES + EXPLORATEUR] OPÉRATIONNEL SUR LE PORT {PORT}")
        print(">>> Affichage en GIGAOCTETS et POURCENTAGES activé.")
        print(">>> En attente de requêtes (CTRL+C pour arrêter)...")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n>>> Arrêt du pont système.")
    except Exception as e:
        print(f">>> ERREUR CRITIQUE : {e}")