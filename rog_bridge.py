import psutil
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import urllib.parse
import sys
import GPUtil  # <--- Ajouté

# --- CONFIGURATION INITIALE ---
last_net_stats = psutil.net_io_counters()
last_time = time.time()

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global last_net_stats, last_time
        
        if self.path.startswith('/open'):
            try:
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
            except Exception:
                self.send_response(500)
                self.end_headers()
                return

        current_time = time.time()
        interval = max(0.1, current_time - last_time)
        current_net = psutil.net_io_counters()
        
        bytes_in = (current_net.bytes_recv - last_net_stats.bytes_recv) / interval
        bytes_out = (current_net.bytes_sent - last_net_stats.bytes_sent) / interval
        
        cpu_usage = psutil.cpu_percent(interval=None)
        ram_usage = psutil.virtual_memory().percent

        # --- NOUVEAU : CALCUL GPU ---
        gpu_stats = {"load": 0, "temp": 0, "vram": 0}
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                g = gpus[0] # Prend la carte principale
                gpu_stats["load"] = round(g.load * 100, 1)
                gpu_stats["temp"] = g.temperature
                gpu_stats["vram"] = round(g.memoryUtil * 100, 1)
        except:
            pass

        def get_disk_info(path):
            try:
                usage = psutil.disk_usage(path)
                return {
                    "percent": usage.percent,
                    "used": round(usage.used / (1024**3), 1),
                    "total": round(usage.total / (1024**3), 0)
                }
            except: return {"percent": 0, "used": 0, "total": 0}

        data = {
            "net": {"in": round(bytes_in / 1024, 2), "out": round(bytes_out / 1024, 2)},
            "performance": {
                "cpu": cpu_usage, 
                "ram": ram_usage,
                "gpu": gpu_stats # <--- Envoyé au Dashboard
            },
            "disks": {
                "c": get_disk_info('C:'),
                "e": get_disk_info('E:'),
                "f": get_disk_info('F:')
            }
        }

        last_net_stats, last_time = current_net, current_time

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') 
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args): return 

if __name__ == "__main__":
    try:
        print(">>> DEMARRAGE DU PONT ROG FULL GPU [OK]")
        server = HTTPServer(('localhost', 9999), DashboardHandler)
        print(">>> CONNECTE AU PORT 9999 [OK]")
        server.serve_forever()
    except Exception as e:
        print(f"Erreur : {e}")
        input()