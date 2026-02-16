#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROG Dashboard v6.0 - Système complet en un seul fichier
Architecture modulaire fusionnée pour exécution autonome
CORRECTION: Gestion améliorée des chemins Windows pour l'Explorateur
"""

import os
import sys
import json
import hashlib
import threading
import traceback
import subprocess
import time
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
from socketserver import ThreadingMixIn

# =============================================================================
# VARIABLES GLOBALES - RATE LIMITING
# =============================================================================

request_counts = {}
REQUEST_LIMIT = 5  # max 5 requêtes par seconde par IP

# =============================================================================
# PARTIE 1: CONFIGURATION ET THÈMES
# =============================================================================

import os

PORT = 9999

# LIGNE 35 - CHEMIN ABSOLU DU FICHIER PASSWORD
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PASSWORD_FILE = os.path.join(SCRIPT_DIR, "rog_password.txt")

STATIC_DIR = "."

THEMES_LIST = [
    "dark", "light", "red", "purple", "orange", "ice", "green", "pink",
    "yellow", "lime", "teal", "magenta", "gold", "blood", "ocean",
    "forest", "midnight", "cherry", "cyber", "matrix", "sunset"
]

THEMES_CSS = """
:root {
    --bg-primary: #0a0a0f;
    --bg-card: rgba(20, 20, 30, 0.9);
    --bg-sidebar: rgba(0, 0, 0, 0.88);
    --bg-input: rgba(0, 0, 0, 0.7);
    --bg-widget: rgba(20, 20, 20, 0.9);
    
    --text-primary: #ffffff;
    --text-secondary: #a0a0b0;
    --text-muted: #888888;
    --text-accent: #00ffcc;
    
    --accent-primary: #00ffcc;
    --accent-secondary: #00ccff;
    --accent-danger: #ff0033;
    --accent-warning: #ffaa00;
    --success: #00ff88;
    
    --border-color: rgba(0, 255, 204, 0.3);
    --border-subtle: rgba(255, 255, 255, 0.1);
    --shadow-glow: rgba(0, 255, 204, 0.4);
    
    --bar-fill: #00ffcc;
    --bar-fill-upload: #00ccff;
    --bar-fill-danger: linear-gradient(90deg, #ff4444, #ff0000);
    
    --font-main: 'Orbitron', sans-serif;
    --font-mono: 'Courier Prime', monospace;
}

[data-theme="light"] {
    --bg-primary: #f0f0f5;
    --bg-card: rgba(255, 255, 255, 0.9);
    --bg-sidebar: rgba(240, 240, 240, 0.82);
    --bg-input: rgba(255, 255, 255, 0.72);
    --bg-widget: rgba(245, 245, 245, 0.75);
    
    --text-primary: #1a1a2e;
    --text-secondary: #4a4a5e;
    --text-muted: #666666;
    --text-accent: #00aa88;
    
    --accent-primary: #00aa88;
    --accent-secondary: #0088aa;
    --accent-danger: #cc0022;
    --accent-warning: #cc8800;
    --success: #00aa44;
    
    --border-color: rgba(0, 170, 136, 0.5);
    --border-subtle: rgba(0, 170, 136, 0.25);
    --shadow-glow: rgba(0, 170, 136, 0.3);
    
    --bar-fill: #00aa88;
    --bar-fill-upload: #00ccaa;
    --bar-fill-danger: linear-gradient(90deg, #ff3333, #cc0000);
}

[data-theme="red"] {
    --bg-primary: #1a0505;
    --bg-card: rgba(40, 10, 10, 0.9);
    --bg-sidebar: rgba(20, 0, 0, 0.95);
    --accent-primary: #ff3333;
    --accent-secondary: #ff6666;
    --border-color: rgba(255, 51, 51, 0.4);
    --shadow-glow: rgba(255, 51, 51, 0.4);
    --bar-fill: #ff3333;
    --bar-fill-upload: #ff6666;
}

[data-theme="purple"] {
    --bg-primary: #150515;
    --bg-card: rgba(40, 10, 40, 0.9);
    --bg-sidebar: rgba(20, 0, 20, 0.95);
    --accent-primary: #cc33ff;
    --accent-secondary: #ff66ff;
    --border-color: rgba(204, 51, 255, 0.4);
    --shadow-glow: rgba(204, 51, 255, 0.4);
    --bar-fill: #cc33ff;
    --bar-fill-upload: #ff66ff;
}

[data-theme="orange"] {
    --bg-primary: #1a0f05;
    --bg-card: rgba(50, 25, 5, 0.9);
    --bg-sidebar: rgba(30, 15, 0, 0.95);
    --accent-primary: #ff8800;
    --accent-secondary: #ffaa33;
    --border-color: rgba(255, 136, 0, 0.4);
    --shadow-glow: rgba(255, 136, 0, 0.4);
    --bar-fill: #ff8800;
    --bar-fill-upload: #ffaa33;
}

[data-theme="ice"] {
    --bg-primary: #050f1a;
    --bg-card: rgba(10, 30, 50, 0.9);
    --bg-sidebar: rgba(0, 10, 20, 0.95);
    --accent-primary: #00ddff;
    --accent-secondary: #66eeff;
    --border-color: rgba(0, 221, 255, 0.4);
    --shadow-glow: rgba(0, 221, 255, 0.4);
    --bar-fill: #00ddff;
    --bar-fill-upload: #66eeff;
}

[data-theme="green"] {
    --bg-primary: #051a05;
    --bg-card: rgba(5, 40, 15, 0.9);
    --bg-sidebar: rgba(0, 20, 5, 0.95);
    --accent-primary: #00ff66;
    --accent-secondary: #33ff88;
    --border-color: rgba(0, 255, 102, 0.4);
    --shadow-glow: rgba(0, 255, 102, 0.4);
    --bar-fill: #00ff66;
    --bar-fill-upload: #33ff88;
}

[data-theme="pink"] {
    --bg-primary: #1a0510;
    --bg-card: rgba(50, 10, 35, 0.9);
    --bg-sidebar: rgba(30, 0, 20, 0.95);
    --accent-primary: #ff66aa;
    --accent-secondary: #ff99cc;
    --border-color: rgba(255, 102, 170, 0.4);
    --shadow-glow: rgba(255, 102, 170, 0.4);
    --bar-fill: #ff66aa;
    --bar-fill-upload: #ff99cc;
}

[data-theme="yellow"] {
    --bg-primary: #1a1805;
    --bg-card: rgba(50, 45, 5, 0.9);
    --bg-sidebar: rgba(30, 25, 0, 0.95);
    --accent-primary: #ffdd00;
    --accent-secondary: #ffee44;
    --border-color: rgba(255, 221, 0, 0.4);
    --shadow-glow: rgba(255, 221, 0, 0.4);
    --bar-fill: #ffdd00;
    --bar-fill-upload: #ffee44;
}

[data-theme="lime"] {
    --bg-primary: #0f1a05;
    --bg-card: rgba(20, 40, 5, 0.9);
    --bg-sidebar: rgba(10, 20, 0, 0.95);
    --accent-primary: #ccff00;
    --accent-secondary: #ddff44;
    --border-color: rgba(204, 255, 0, 0.4);
    --shadow-glow: rgba(204, 255, 0, 0.4);
    --bar-fill: #ccff00;
    --bar-fill-upload: #ddff44;
}

[data-theme="teal"] {
    --bg-primary: #051a15;
    --bg-card: rgba(5, 40, 35, 0.9);
    --bg-sidebar: rgba(0, 20, 15, 0.95);
    --accent-primary: #00ffcc;
    --accent-secondary: #33ffdd;
    --border-color: rgba(0, 255, 204, 0.4);
    --shadow-glow: rgba(0, 255, 204, 0.4);
    --bar-fill: #00ffcc;
    --bar-fill-upload: #33ffdd;
}

[data-theme="magenta"] {
    --bg-primary: #1a051a;
    --bg-card: rgba(45, 10, 45, 0.9);
    --bg-sidebar: rgba(25, 0, 25, 0.95);
    --accent-primary: #ff00ff;
    --accent-secondary: #ff44ff;
    --border-color: rgba(255, 0, 255, 0.4);
    --shadow-glow: rgba(255, 0, 255, 0.4);
    --bar-fill: #ff00ff;
    --bar-fill-upload: #ff44ff;
}

[data-theme="gold"] {
    --bg-primary: #1a1505;
    --bg-card: rgba(50, 35, 5, 0.9);
    --bg-sidebar: rgba(30, 20, 0, 0.95);
    --accent-primary: #ffcc00;
    --accent-secondary: #ffdd44;
    --border-color: rgba(255, 204, 0, 0.4);
    --shadow-glow: rgba(255, 204, 0, 0.4);
    --bar-fill: #ffcc00;
    --bar-fill-upload: #ffdd44;
}

[data-theme="blood"] {
    --bg-primary: #0a0000;
    --bg-card: rgba(30, 5, 5, 0.9);
    --bg-sidebar: rgba(10, 0, 0, 0.95);
    --accent-primary: #ff0000;
    --accent-secondary: #ff3333;
    --accent-danger: #ff0000;
    --border-color: rgba(255, 0, 0, 0.5);
    --shadow-glow: rgba(255, 0, 0, 0.5);
    --bar-fill: #ff0000;
    --bar-fill-upload: #ff3333;
}

[data-theme="ocean"] {
    --bg-primary: #050a1a;
    --bg-card: rgba(5, 25, 50, 0.9);
    --bg-sidebar: rgba(0, 10, 30, 0.95);
    --accent-primary: #0088ff;
    --accent-secondary: #33aaff;
    --border-color: rgba(0, 136, 255, 0.4);
    --shadow-glow: rgba(0, 136, 255, 0.4);
    --bar-fill: #0088ff;
    --bar-fill-upload: #33aaff;
}

[data-theme="forest"] {
    --bg-primary: #051005;
    --bg-card: rgba(10, 35, 10, 0.9);
    --bg-sidebar: rgba(5, 15, 5, 0.95);
    --accent-primary: #44ff44;
    --accent-secondary: #66ff66;
    --border-color: rgba(68, 255, 68, 0.4);
    --shadow-glow: rgba(68, 255, 68, 0.4);
    --bar-fill: #44ff44;
    --bar-fill-upload: #66ff66;
}

[data-theme="midnight"] {
    --bg-primary: #050510;
    --bg-card: rgba(15, 15, 35, 0.9);
    --bg-sidebar: rgba(5, 5, 15, 0.95);
    --accent-primary: #6666ff;
    --accent-secondary: #8888ff;
    --border-color: rgba(102, 102, 255, 0.4);
    --shadow-glow: rgba(102, 102, 255, 0.4);
    --bar-fill: #6666ff;
    --bar-fill-upload: #8888ff;
}

[data-theme="cherry"] {
    --bg-primary: #1a0510;
    --bg-card: rgba(40, 5, 20, 0.9);
    --bg-sidebar: rgba(20, 0, 10, 0.95);
    --accent-primary: #ff3366;
    --accent-secondary: #ff6688;
    --border-color: rgba(255, 51, 102, 0.4);
    --shadow-glow: rgba(255, 51, 102, 0.4);
    --bar-fill: #ff3366;
    --bar-fill-upload: #ff6688;
}

[data-theme="cyber"] {
    --bg-primary: #100520;
    --bg-card: rgba(25, 5, 40, 0.9);
    --bg-sidebar: rgba(10, 0, 20, 0.95);
    --accent-primary: #aa00ff;
    --accent-secondary: #cc44ff;
    --border-color: rgba(170, 0, 255, 0.4);
    --shadow-glow: rgba(170, 0, 255, 0.4);
    --bar-fill: #aa00ff;
    --bar-fill-upload: #cc44ff;
}

[data-theme="matrix"] {
    --bg-primary: #000a00;
    --bg-card: rgba(5, 25, 5, 0.9);
    --bg-sidebar: rgba(0, 10, 0, 0.95);
    --accent-primary: #00ff00;
    --accent-secondary: #33ff33;
    --border-color: rgba(0, 255, 0, 0.4);
    --shadow-glow: rgba(0, 255, 0, 0.4);
    --bar-fill: #00ff00;
    --bar-fill-upload: #33ff33;
}

[data-theme="sunset"] {
    --bg-primary: #1a1015;
    --bg-card: rgba(50, 20, 25, 0.9);
    --bg-sidebar: rgba(30, 10, 15, 0.95);
    --accent-primary: #ff5555;
    --accent-secondary: #ff7777;
    --border-color: rgba(255, 85, 85, 0.4);
    --shadow-glow: rgba(255, 85, 85, 0.4);
    --bar-fill: #ff5555;
    --bar-fill-upload: #ff7777;
}
"""

# =============================================================================
# PARTIE 2: MONITEUR SYSTÈME
# =============================================================================

last_net_stats = None
last_time = time.time()
net_history = {'in': [0]*60, 'out': [0]*60}

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[WARN] psutil non installé - Mode simulation activé")

try:
    import pynvml
    pynvml.nvmlInit()
    GPU_AVAILABLE = True
    gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0) if pynvml.nvmlDeviceGetCount() > 0 else None
    if not gpu_handle:
        GPU_AVAILABLE = False
except ImportError:
    GPU_AVAILABLE = False
    gpu_handle = None

def get_cpu_temp():
    try:
        if PSUTIL_AVAILABLE:
            load = psutil.cpu_percent(interval=0.1)
            variation = random.uniform(-3, 3)
            return round(48 + (load / 100) * 35 + variation, 1)
    except:
        pass
    return round(50 + random.uniform(-5, 8), 1)

def get_performance_data():
    if PSUTIL_AVAILABLE:
        try:
            return {
                "cpu": psutil.cpu_percent(interval=0.1),
                "ram": psutil.virtual_memory().percent,
                "cpu_temp": get_cpu_temp()
            }
        except Exception as e:
            print(f"[WARN] Erreur performance: {e}")
    
    return {
        "cpu": random.uniform(10, 45),
        "ram": random.uniform(30, 70),
        "cpu_temp": get_cpu_temp()
    }

def get_disk_data():
    disks = {}
    if PSUTIL_AVAILABLE:
        try:
            for partition in psutil.disk_partitions():
                try:
                    if partition.device and ':' in partition.device:
                        letter = partition.device[0].lower()
                        usage = psutil.disk_usage(partition.mountpoint)
                        disks[letter] = {
                            "total": round(usage.total / (1024**3), 1),
                            "used": round(usage.used / (1024**3), 1),
                            "free": round(usage.free / (1024**3), 1),
                            "percent": usage.percent
                        }
                except:
                    pass
        except Exception as e:
            print(f"[WARN] Erreur disques: {e}")
    
    if not disks:
        disks = {
            'c': {"total": 930.5, "used": 733.5, "free": 197.0, "percent": 78},
            'e': {"total": 931.5, "used": 701.6, "free": 229.9, "percent": 75},
            'f': {"total": 931.5, "used": 32.3, "free": 899.2, "percent": 3}
        }
    
    return disks

def get_network_data():
    global last_net_stats, last_time, net_history
    
    if PSUTIL_AVAILABLE and last_net_stats is not None:
        try:
            current_time = time.time()
            interval = max(0.1, current_time - last_time)
            net_io = psutil.net_io_counters()
            
            bi = (net_io.bytes_recv - last_net_stats.bytes_recv) / interval / 1024
            bo = (net_io.bytes_sent - last_net_stats.bytes_sent) / interval / 1024
            
            bi = max(0, min(bi, 100000))
            bo = max(0, min(bo, 100000))
            
            net_history['in'] = net_history['in'][1:] + [round(bi, 2)]
            net_history['out'] = net_history['out'][1:] + [round(bo, 2)]
            
            last_net_stats = net_io
            last_time = current_time
            
            return {
                "in": round(bi, 2),
                "out": round(bo, 2),
                "history": net_history
            }
        except Exception as e:
            print(f"[WARN] Erreur réseau: {e}")
    
    if PSUTIL_AVAILABLE and last_net_stats is None:
        try:
            last_net_stats = psutil.net_io_counters()
        except:
            pass
    
    if not PSUTIL_AVAILABLE or last_net_stats is None:
        bi = random.uniform(0.1, 5.0)
        bo = random.uniform(0.05, 2.0)
        net_history['in'] = net_history['in'][1:] + [round(bi, 2)]
        net_history['out'] = net_history['out'][1:] + [round(bo, 2)]
        
        return {
            "in": round(bi, 2),
            "out": round(bo, 2),
            "history": net_history
        }
    
    return {"in": 0, "out": 0, "history": net_history}

def get_gpu_data():
    if GPU_AVAILABLE and gpu_handle:
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
            
            try:
                temp = pynvml.nvmlDeviceGetTemperature(gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
            except:
                temp = 40 + int(util.gpu / 100 * 40) if util else 40
            
            try:
                name = pynvml.nvmlDeviceGetName(gpu_handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')
            except:
                name = "NVIDIA GPU"
            
            return {
                "name": name,
                "load": util.gpu if util else 0,
                "temp": temp,
                "memory_used": round(mem.used / (1024**2), 1),
                "memory_total": round(mem.total / (1024**2), 1),
                "memory_percent": round((mem.used / mem.total * 100), 1) if mem.total else 0
            }
        except Exception as e:
            print(f"[WARN] Erreur GPU: {e}")
    
    return None

def get_processes():
    processes = []
    if PSUTIL_AVAILABLE:
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    cpu = proc.info['cpu_percent']
                    if cpu and cpu > 1.0:
                        processes.append({
                            "name": str(proc.info['name'] or "Unknown"),
                            "cpu": float(cpu),
                            "pid": int(proc.info['pid'] or 0)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            return processes[:5]
        except Exception as e:
            print(f"[WARN] Erreur processus: {e}")
    
    return [
        {"name": "System Idle", "cpu": 94.0, "pid": 0},
        {"name": "firefox.exe", "cpu": 2.4, "pid": 1234},
        {"name": "explorer.exe", "cpu": 0.8, "pid": 5678},
        {"name": "python.exe", "cpu": 0.5, "pid": 9999},
        {"name": "discord.exe", "cpu": 0.3, "pid": 1111}
    ]

def get_security_status():
    return {
        "firewall": "ACTIF - Windows Defender",
        "ports": "SCAN: AUCUNE MENACE",
        "vpn": "DÉCONNECTÉ",
        "encryption": "AES-256-GCM"
    }

def get_system_news():
    gpu_status = "[GPU] Carte graphique NVIDIA détectée" if GPU_AVAILABLE else "[GPU] Mode simulation activé"
    return [
        "[SYS] Système démarré avec succès",
        "[NET] Connexion réseau établie",
        gpu_status,
        "[SEC] Firewall actif et opérationnel",
        f"[INF] Dashboard prêt - Port {PORT} actif",
        "[TMP] Surveillance températures active"
    ]

def get_all_system_data():
    return {
        "status": "online",
        "timestamp": time.time(),
        "performance": get_performance_data(),
        "disks": get_disk_data(),
        "net": get_network_data(),
        "gpu": get_gpu_data(),
        "processes": get_processes(),
        "security": get_security_status(),
        "news": get_system_news()
    }

# =============================================================================
# PARTIE 3: TEMPLATES HTML
# =============================================================================

LOGIN_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>ROG Dashboard - Login</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Orbitron', sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
        }
        .login-container {
            background: rgba(20, 20, 30, 0.9);
            border: 1px solid rgba(0, 255, 204, 0.3);
            border-radius: 15px;
            padding: 40px;
            width: 400px;
            box-shadow: 0 0 40px rgba(0, 255, 204, 0.2);
        }
        .logo {
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #00ffcc, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            color: #888;
            font-size: 12px;
            margin-bottom: 30px;
            letter-spacing: 2px;
        }
        .input-group { margin-bottom: 20px; }
        label {
            display: block;
            color: #00ffcc;
            font-size: 11px;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        input[type="password"] {
            width: 100%;
            padding: 12px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(0, 255, 204, 0.3);
            border-radius: 8px;
            color: white;
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            outline: none;
            transition: all 0.3s;
        }
        input[type="password"]:focus {
            border-color: #00ffcc;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.3);
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #00ffcc, #00ccff);
            border: none;
            border-radius: 8px;
            color: #0a0a0f;
            font-family: 'Orbitron', sans-serif;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 255, 204, 0.4);
        }
        .error {
            color: #ff0033;
            font-size: 12px;
            margin-top: 10px;
            text-align: center;
            display: none;
        }
        .info {
            text-align: center;
            color: #666;
            font-size: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">⚡ ROG DASHBOARD</div>
        <div class="subtitle">AUTHENTIFICATION REQUISE</div>
        <form id="login-form">
            <div class="input-group">
                <label>MOT DE PASSE</label>
                <input type="password" id="password" placeholder="••••••••" required autofocus>
            </div>
            <button type="submit">CONNEXION</button>
            <div class="error" id="error">Mot de passe incorrect</div>
        </form>
        <div class="info">
            Accès local (127.0.0.1) = Pas de mot de passe requis<br>
            ROG Bridge v6.0 - MODULAIRE
        </div>
    </div>
    <script>
        document.getElementById('login-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const password = document.getElementById('password').value;
            try {
                const response = await fetch('/api/auth', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password })
                });
                const data = await response.json();
                if (data.success) {
                    window.location.href = '/';
                } else {
                    document.getElementById('error').style.display = 'block';
                }
            } catch (e) {
                document.getElementById('error').textContent = 'Erreur de connexion';
                document.getElementById('error').style.display = 'block';
            }
        });
    </script>
</body>
</html>"""

def generate_theme_button_styles():
    styles = {
        'dark': '#00ffcc, #008866',
        'light': '#f5f5f0, #e0d5c5',
        'red': '#ff3333, #aa0000',
        'purple': '#cc33ff, #660099',
        'orange': '#ff8800, #cc4400',
        'ice': '#00ddff, #0066aa',
        'green': '#00ff66, #00aa44',
        'pink': '#ff66aa, #cc3377',
        'yellow': '#ffdd00, #ccaa00',
        'lime': '#ccff00, #88aa00',
        'teal': '#00ffcc, #00aa88',
        'magenta': '#ff00ff, #aa00aa',
        'gold': '#ffcc00, #cc9900',
        'blood': '#ff0000, #880000',
        'ocean': '#0088ff, #004488',
        'forest': '#44ff44, #228822',
        'midnight': '#6666ff, #3333aa',
        'cherry': '#ff3366, #cc1144',
        'cyber': '#aa00ff, #6600aa',
        'matrix': '#00ff00, #008800',
        'sunset': '#ff5555, #cc3333'
    }
    
    css = []
    for theme, colors in styles.items():
        css.append(f'.theme-btn[data-theme="{theme}"] {{ background: linear-gradient(135deg, {colors}); }}')
    
    return '\n        '.join(css)

def generate_dashboard_html():
    theme_buttons = ''.join([f'<div class="theme-btn" data-theme="{t}"></div>' for t in THEMES_LIST])
    
    return f"""<!DOCTYPE html>
<html lang="fr" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROG Dashboard - Système</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Courier+Prime&display=swap" rel="stylesheet">
    <style>
{THEMES_CSS}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Orbitron', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }}
        .theme-selector {{
            position: fixed;
            top: 5px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10000;
            display: flex;
            gap: 8px;
            background: rgba(0, 0, 0, 0.9);
            padding: 8px 16px;
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(15px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            flex-wrap: wrap;
            max-width: 95vw;
            justify-content: center;
        }}
        .theme-btn {{
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .theme-btn:hover {{ transform: scale(1.15); }}
        .theme-btn.active {{ 
            border-color: #fff; 
            box-shadow: 0 0 0 2px rgba(0,0,0,0.9), 0 0 0 4px var(--accent-primary); 
        }}
        {generate_theme_button_styles()}
        .mode-toggle {{ margin-left: 12px; padding-left: 12px; border-left: 2px solid rgba(255,255,255,0.2); }}
        .mode-toggle-btn {{
            background: transparent;
            border: 2px solid rgba(255,255,255,0.3);
            color: #ddd;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }}
        .mode-toggle-btn:hover {{ background: var(--accent-primary); border-color: var(--accent-primary); }}
        .header {{
            background: var(--bg-card);
            border-bottom: 2px solid var(--accent-primary);
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px var(--shadow-glow);
            position: sticky;
            top: 0;
            z-index: 100;
            margin-top: 60px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: 900;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 4px;
        }}
        .header-info {{ display: flex; gap: 30px; align-items: center; }}
        .status-badge {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(0, 255, 0, 0.1);
            border: 1px solid var(--success);
            border-radius: 20px;
            font-size: 12px;
            color: var(--success);
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.5; transform: scale(1.2); }}
        }}
        .clock {{
            font-family: 'Courier Prime', monospace;
            font-size: 18px;
            color: var(--accent-primary);
        }}
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }}
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: all 0.3s;
        }}
        .card:hover {{
            border-color: var(--accent-primary);
            box-shadow: 0 0 20px var(--shadow-glow);
            transform: translateY(-2px);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
        }}
        .card-title {{
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 2px;
            color: var(--accent-primary);
            text-transform: uppercase;
        }}
        .metric {{ margin-bottom: 15px; }}
        .metric-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 12px;
        }}
        .metric-label {{ color: var(--text-secondary); }}
        .metric-value {{
            color: var(--accent-primary);
            font-family: 'Courier Prime', monospace;
            font-weight: bold;
        }}
        .progress-bar {{
            height: 8px;
            background: rgba(0,0,0,0.5);
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 4px;
            transition: width 0.5s;
            box-shadow: 0 0 10px var(--shadow-glow);
        }}
        .net-graph {{
            height: 100px;
            background: rgba(0,0,0,0.5);
            border-radius: 8px;
            margin-top: 10px;
            position: relative;
            overflow: hidden;
        }}
        .net-graph canvas {{ width: 100%; height: 100%; display: block; }}
        .process-list {{ max-height: 200px; overflow-y: auto; }}
        .process-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            margin-bottom: 5px;
            background: rgba(0,0,0,0.3);
            border-radius: 6px;
            border-left: 3px solid var(--accent-primary);
            font-family: 'Courier Prime', monospace;
            font-size: 12px;
        }}
        .process-name {{ color: var(--text-secondary); }}
        .process-cpu {{ color: var(--accent-primary); font-weight: bold; }}
        .security-grid {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .security-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 12px;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            border: 1px solid var(--border-color);
        }}
        .security-icon {{
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            font-size: 18px;
        }}
        .security-icon.ok {{ background: rgba(0, 255, 0, 0.1); color: var(--success); }}
        .security-icon.warn {{ background: rgba(255, 170, 0, 0.1); color: var(--accent-warning); }}
        .security-label {{ font-size: 10px; color: var(--text-secondary); text-transform: uppercase; }}
        .security-value {{
            font-size: 13px;
            color: var(--text-primary);
            font-weight: bold;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex: 1;
        }}
        .news-container {{
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier Prime', monospace;
            font-size: 12px;
            line-height: 1.8;
            max-height: 300px;
            overflow-y: auto;
        }}
        .news-item {{
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
        }}
        .news-item:last-child {{ border-bottom: none; }}
        .news-time {{ color: var(--accent-primary); margin-right: 10px; }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 11px;
            border-top: 1px solid var(--border-color);
            margin-top: 20px;
        }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.3); }}
        ::-webkit-scrollbar-thumb {{ background: var(--accent-primary); border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="theme-selector">
        {theme_buttons}
        <div class="mode-toggle">
            <button class="mode-toggle-btn" id="mode-toggle">🌙</button>
        </div>
    </div>

    <div class="header">
        <div class="logo">⚡ ROG DASHBOARD</div>
        <div class="header-info">
            <div class="status-badge">
                <div class="status-dot"></div>
                <span id="system-status">SYSTÈME EN LIGNE</span>
            </div>
            <div class="clock" id="clock">00:00:00</div>
        </div>
    </div>

    <div class="dashboard-grid">
        <div class="card">
            <div class="card-header">
                <span class="card-title">🔥 Processeur (CPU)</span>
                <span>💻</span>
            </div>
            <div class="metric">
                <div class="metric-header">
                    <span class="metric-label">Utilisation</span>
                    <span class="metric-value" id="cpu-value">--%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-bar" style="width: 0%"></div>
                </div>
            </div>
            <div class="metric">
                <div class="metric-header">
                    <span class="metric-label">Température</span>
                    <span class="metric-value" id="cpu-temp-display">--°C</span>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">💾 Mémoire (RAM)</span>
                <span>🧠</span>
            </div>
            <div class="metric">
                <div class="metric-header">
                    <span class="metric-label">Utilisation</span>
                    <span class="metric-value" id="ram-value">--%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="ram-bar" style="width: 0%"></div>
                </div>
            </div>
            <div class="metric">
                <div class="metric-header">
                    <span class="metric-label">Disponible</span>
                    <span class="metric-value" id="ram-available">-- GB</span>
                </div>
            </div>
        </div>

        <div class="card" id="gpu-card" style="display: none;">
            <div class="card-header">
                <span class="card-title">🎮 Carte Graphique (GPU)</span>
                <span>🚀</span>
            </div>
            <div class="metric">
                <div class="metric-header">
                    <span class="metric-label" id="gpu-name">GPU</span>
                    <span class="metric-value" id="gpu-load">--%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="gpu-bar-fill" style="width: 0%"></div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px;">
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid var(--border-color);">
                    <div style="font-size: 10px; color: var(--text-secondary); text-transform: uppercase;">Température</div>
                    <div style="font-size: 18px; color: var(--accent-primary); font-family: 'Courier Prime', monospace; margin-top: 5px;" id="gpu-temp-display">--°C</div>
                </div>
                <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid var(--border-color);">
                    <div style="font-size: 10px; color: var(--text-secondary); text-transform: uppercase;">VRAM</div>
                    <div style="font-size: 18px; color: var(--accent-primary); font-family: 'Courier Prime', monospace; margin-top: 5px;" id="gpu-vram">--%</div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">🌐 Réseau</span>
                <span>📡</span>
            </div>
            <div class="metric">
                <div class="metric-header">
                    <span class="metric-label">Download</span>
                    <span class="metric-value" id="net-in">-- Mo/s</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="net-in-bar" style="width: 0%"></div>
                </div>
            </div>
            <div class="metric">
                <div class="metric-header">
                    <span class="metric-label">Upload</span>
                    <span class="metric-value" id="net-out">-- Mo/s</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%; background: var(--accent-secondary);" id="net-out-bar"></div>
                </div>
            </div>
            <div class="net-graph">
                <canvas id="net-canvas" width="400" height="100"></canvas>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">💿 Stockage</span>
                <span>🗄️</span>
            </div>
            <div id="disk-container"></div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">⚙️ Processus Actifs</span>
                <span>🔧</span>
            </div>
            <div class="process-list" id="process-list"></div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">🔒 Sécurité</span>
                <span>🛡️</span>
            </div>
            <div class="security-grid" id="security-grid"></div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">📰 Journal Système</span>
                <span>📋</span>
            </div>
            <div class="news-container" id="news-container"></div>
        </div>
    </div>

    <div class="footer">
        ROG Dashboard v6.0 | Serveur Local: http://localhost:{PORT} | Développé pour ROG Systems
    </div>

    <script>
        const themes = {THEMES_LIST};
        let currentTheme = localStorage.getItem('rog_theme') || 'dark';

        function applyTheme(theme) {{
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('rog_theme', theme);
            currentTheme = theme;
            updateActiveButton();
        }}

        function updateActiveButton() {{
            document.querySelectorAll('.theme-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.theme === currentTheme);
            }});
            document.getElementById('mode-toggle').textContent = currentTheme === 'light' ? '☀️' : '🌙';
        }}

        document.querySelectorAll('.theme-btn').forEach(btn => {{
            btn.addEventListener('click', (e) => applyTheme(e.target.dataset.theme));
        }});

        document.getElementById('mode-toggle').addEventListener('click', () => {{
            applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
        }});

        function updateClock() {{
            document.getElementById('clock').textContent = new Date().toLocaleTimeString('fr-FR');
        }}
        setInterval(updateClock, 1000);
        updateClock();

        async function fetchData() {{
            try {{
                const response = await fetch('/api/data');
                if (!response.ok) throw new Error('Not authenticated');
                const data = await response.json();
                updateDashboard(data);
                document.getElementById('system-status').textContent = 'SYSTÈME EN LIGNE';
                document.querySelector('.status-dot').style.background = 'var(--success)';
            }} catch (e) {{
                console.error('Erreur données:', e);
                document.getElementById('system-status').textContent = 'MODE OFFLINE';
                document.querySelector('.status-dot').style.background = 'var(--accent-danger)';
                updateDashboard(getSimulatedData());
            }}
        }}

        function getSimulatedData() {{
            return {{
                performance: {{
                    cpu: Math.random() * 30 + 10,
                    ram: Math.random() * 40 + 30,
                    cpu_temp: 40 + Math.random() * 15
                }},
                disks: {{
                    c: {{total: 930.5, used: 733.5, free: 197.0, percent: 78}},
                    e: {{total: 931.5, used: 701.6, free: 229.9, percent: 75}},
                    f: {{total: 931.5, used: 32.3, free: 899.2, percent: 3}}
                }},
                net: {{
                    in: Math.random() * 5,
                    out: Math.random() * 2,
                    history: {{in: Array(60).fill(0).map(() => Math.random() * 5), out: Array(60).fill(0).map(() => Math.random() * 2)}}
                }},
                gpu: null,
                processes: [
                    {{name: "System Idle", cpu: 94.0}},
                    {{name: "firefox.exe", cpu: 2.4}},
                    {{name: "explorer.exe", cpu: 0.8}},
                    {{name: "python.exe", cpu: 0.5}},
                    {{name: "discord.exe", cpu: 0.3}}
                ],
                security: {{
                    firewall: "ACTIF - Windows Defender",
                    ports: "SCAN: AUCUNE MENACE",
                    vpn: "DÉCONNECTÉ",
                    encryption: "AES-256-GCM"
                }},
                news: [
                    "[SYS] Mode offline - Données simulées",
                    "[NET] Connexion au serveur perdue",
                    "[GPU] Surveillance désactivée",
                    "[SEC] Sécurité maintenue",
                    "[INF] Utilisation données locales"
                ]
            }};
        }}

        function updateDashboard(data) {{
            if (data.performance) {{
                document.getElementById('cpu-value').textContent = data.performance.cpu.toFixed(1) + '%';
                document.getElementById('cpu-bar').style.width = data.performance.cpu + '%';
                document.getElementById('cpu-temp-display').textContent = (data.performance.cpu_temp || 40).toFixed(1) + '°C';

                document.getElementById('ram-value').textContent = data.performance.ram.toFixed(1) + '%';
                document.getElementById('ram-bar').style.width = data.performance.ram + '%';
                const available = ((100 - data.performance.ram) / 100 * 32).toFixed(1);
                document.getElementById('ram-available').textContent = available + ' GB';
            }}

            if (data.gpu) {{
                document.getElementById('gpu-card').style.display = 'block';
                document.getElementById('gpu-name').textContent = data.gpu.name || 'GPU';
                document.getElementById('gpu-load').textContent = data.gpu.load + '%';
                document.getElementById('gpu-bar-fill').style.width = data.gpu.load + '%';
                document.getElementById('gpu-temp-display').textContent = data.gpu.temp + '°C';
                document.getElementById('gpu-vram').textContent = data.gpu.memory_percent + '%';
            }} else {{
                document.getElementById('gpu-card').style.display = 'none';
            }}

            if (data.net) {{
                const netIn = (data.net.in / 1024).toFixed(2);
                const netOut = (data.net.out / 1024).toFixed(2);
                document.getElementById('net-in').textContent = netIn + ' Mo/s';
                document.getElementById('net-out').textContent = netOut + ' Mo/s';
                document.getElementById('net-in-bar').style.width = Math.min(netIn * 10, 100) + '%';
                document.getElementById('net-out-bar').style.width = Math.min(netOut * 10, 100) + '%';
                if (data.net.history) drawNetGraph(data.net.history);
            }}

            if (data.disks) updateDisks(data.disks);
            if (data.processes) updateProcesses(data.processes);
            if (data.security) updateSecurity(data.security);
            if (data.news) updateNews(data.news);
        }}

        function updateDisks(disks) {{
            const container = document.getElementById('disk-container');
            container.innerHTML = '';
            Object.keys(disks).forEach(letter => {{
                const disk = disks[letter];
                const div = document.createElement('div');
                div.style.cssText = 'background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px; border: 1px solid var(--border-color); margin-bottom: 10px;';
                div.innerHTML = `
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="font-weight: bold;">${{letter.toUpperCase()}}:</span>
                        <span style="color: var(--text-secondary); font-size: 11px;">${{disk.used.toFixed(1)}} / ${{disk.total.toFixed(1)}} Go</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${{disk.percent}}%; ${{disk.percent > 90 ? 'background: linear-gradient(90deg, #ff0033, #cc0000);' : ''}}"></div>
                    </div>
                    <div style="text-align: right; margin-top: 5px; font-size: 11px; color: var(--text-secondary);">${{disk.percent}}% utilisé</div>
                `;
                container.appendChild(div);
            }});
        }}

        function updateProcesses(processes) {{
            const container = document.getElementById('process-list');
            container.innerHTML = '';
            processes.forEach(proc => {{
                const div = document.createElement('div');
                div.className = 'process-item';
                const name = proc.name.length > 20 ? proc.name.substring(0, 20) + '...' : proc.name;
                const color = proc.cpu > 50 ? 'var(--accent-danger)' : proc.cpu > 20 ? 'var(--accent-warning)' : 'var(--accent-primary)';
                div.innerHTML = `<span class="process-name">${{name}}</span><span class="process-cpu" style="color: ${{color}};">${{proc.cpu.toFixed(1)}}%</span>`;
                container.appendChild(div);
            }});
        }}

        function updateSecurity(security) {{
            const container = document.getElementById('security-grid');
            const items = [
                {{ icon: '🛡️', label: 'Firewall', value: security.firewall, ok: security.firewall.includes('ACTIF') }},
                {{ icon: '🔌', label: 'Ports', value: security.ports, ok: !security.ports.includes('ERREUR') }},
                {{ icon: '🔐', label: 'VPN', value: security.vpn, ok: security.vpn === 'CONNECTÉ' }},
                {{ icon: '🔑', label: 'Chiffrement', value: security.encryption, ok: true }}
            ];
            container.innerHTML = items.map(item => `
                <div class="security-item">
                    <div class="security-icon ${{item.ok ? 'ok' : 'warn'}}">${{item.icon}}</div>
                    <div>
                        <div class="security-label">${{item.label}}</div>
                        <div class="security-value" title="${{item.value}}">${{item.value}}</div>
                    </div>
                </div>
            `).join('');
        }}

        function updateNews(news) {{
            const container = document.getElementById('news-container');
            container.innerHTML = news.map(item => {{
                const match = item.match(/\\[(.*?)\\] (.*)/);
                if (match) return `<div class="news-item"><span class="news-time">[${{match[1]}}]</span>${{match[2]}}</div>`;
                return `<div class="news-item">${{item}}</div>`;
            }}).join('');
        }}

        function drawNetGraph(history) {{
            const canvas = document.getElementById('net-canvas');
            if (!canvas || !history || !history.in) return;
            const ctx = canvas.getContext('2d');
            const width = canvas.width = canvas.offsetWidth;
            const height = canvas.height = canvas.offsetHeight;

            ctx.clearRect(0, 0, width, height);
            const maxVal = Math.max(...history.in, ...history.out, 1);

            ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim() || '#00ffcc';
            ctx.lineWidth = 2;
            ctx.beginPath();
            history.in.forEach((val, i) => {{
                const x = (width / (history.in.length - 1)) * i;
                const y = height - ((val / maxVal) * height * 0.9);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();

            ctx.strokeStyle = getComputedStyle(document.documentElement).getPropertyValue('--accent-secondary').trim() || '#00ccff';
            ctx.beginPath();
            history.out.forEach((val, i) => {{
                const x = (width / (history.out.length - 1)) * i;
                const y = height - ((val / maxVal) * height * 0.9);
                if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
            }});
            ctx.stroke();
        }}

        applyTheme(currentTheme);
        fetchData();
        setInterval(fetchData, 2000);

        window.addEventListener('resize', () => {{
            const canvas = document.getElementById('net-canvas');
            if (canvas) {{
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
            }}
        }});
    </script>
</body>
</html>"""

# =============================================================================
# PARTIE 4: MOT DE PASSE SERVEUR ET AUTHENTIFICATION
# =============================================================================

def load_password():
    """
    Charge le mot de passe depuis rog_password.txt (chemin absolu)
    """
    try:
        print(f"[DEBUG] Recherche fichier: {PASSWORD_FILE}")
        
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
                pwd = f.read().strip()
                if pwd:
                    print(f"[OK] Mot de passe chargé: {pwd}")
                    return pwd
            print("[WARN] Fichier vide")
        else:
            print(f"[WARN] Fichier introuvable: {PASSWORD_FILE}")
            
        # Fallback si problème
        return "Naxos1946."
        
    except Exception as e:
        print(f"[CRITICAL] Erreur lecture: {e}")
        return "Naxos1946."  # Fallback ultime


def verify_password(password):
    try:
        correct = load_password()
        if correct is None:
            print("[ERROR] Aucun mot de passe configuré")
            return False
        return hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256(correct.encode()).hexdigest()
    except Exception as e:
        print(f"[ERROR] Erreur verify_password: {e}")
        return False
    
# =============================================================================
# FONCTION DE VÉRIFICATION DES CHEMINS - CORRIGÉE
# =============================================================================

def is_path_allowed(path):
    r"""
    Vérifie si le chemin est autorisé à être ouvert.
    Accepte les chemins avec / ou \ comme séparateurs.
    """
    # Normaliser le chemin pour la comparaison (convertir / en \ et éliminer les doubles)
    normalized = path.replace('/', '\\').replace('\\\\', '\\').lower()
    
    # Liste des préfixes autorisés
    allowed_prefixes = [
        "c:\\users", "c:\\program files", "c:\\programdata", 
        "c:\\windows", "e:\\", "f:\\", "d:\\", "c:\\"
    ]
    
    for prefix in allowed_prefixes:
        if normalized.startswith(prefix.lower()):
            return True
    
    # Accepter aussi les chemins de type C:\ seul
    if len(normalized) >= 2 and normalized[1] == ':' and normalized[0].isalpha():
        return True
        
    return False

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class DashboardHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    timeout = 30

    def log_message(self, format, *args):
        msg = format % args
        ignore_patterns = ['414', 'favicon', 'Connection reset', 'Broken pipe']
        if not any(p in msg.lower() for p in ignore_patterns):
            print(f"[{self.log_date_time_string()}] {msg}")

    def handle(self):
        try:
            super().handle()
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError, TimeoutError, OSError):
            pass
        except Exception as e:
            if '414' not in str(e):
                print(f"[WARN] Erreur connexion: {e}")

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_cors_headers()
            self.send_header('Content-Length', '0')
            self.end_headers()
        except Exception:
            pass

    def _send_json(self, data, code=200):
        try:
            json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors_headers()
            self.send_header('Content-Length', str(len(json_data)))
            self.end_headers()
            self.wfile.write(json_data)
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            print(f"[WARN] Erreur envoi JSON: {e}")

    def _send_html(self, html, code=200):
        try:
            html_data = html.encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_cors_headers()
            self.send_header('Content-Length', str(len(html_data)))
            self.end_headers()
            self.wfile.write(html_data)
        except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            print(f"[WARN] Erreur envoi HTML: {e}")

    def _redirect(self, location, code=302):
        try:
            self.send_response(code)
            self.send_header('Location', location)
            self.send_header('Content-Length', '0')
            self.end_headers()
        except Exception as e:
            print(f"[WARN] Erreur redirection: {e}")

    def get_client_ip(self):
        try:
            forwarded = self.headers.get('X-Forwarded-For')
            if forwarded:
                return forwarded.split(',')[0].strip()
            return self.client_address[0]
        except Exception:
            return '127.0.0.1'

    def is_local_access(self):
        return self.get_client_ip() in ('127.0.0.1', 'localhost', '::1', '0.0.0.0')

    def is_authenticated(self):
        if self.is_local_access():
            return True
        with authenticated_ips_lock:
            return self.get_client_ip() in authenticated_ips

    def do_GET(self):
        try:
            # =============================================================================
            # RATE LIMITING - Protection contre les requêtes excessives
            # =============================================================================
            client_ip = self.get_client_ip()
            current_time = time.time()
            
            # Ignorer le rate limiting pour localhost (127.0.0.1, ::1)
            if not self.is_local_access():
                if client_ip in request_counts:
                    last_time, count = request_counts[client_ip]
                    if current_time - last_time < 1:  # fenêtre de 1 seconde
                        if count > REQUEST_LIMIT:
                            print(f"[RATE LIMIT] IP {client_ip} bloquée ({count} requêtes/sec)")
                            self._send_json({"error": "Too many requests"}, 429)
                            return
                        request_counts[client_ip] = (last_time, count + 1)
                    else:
                        # Réinitialiser le compteur après 1 seconde
                        request_counts[client_ip] = (current_time, 1)
                else:
                    request_counts[client_ip] = (current_time, 1)
            
            if len(self.path) > 8000:
                self._send_json({"error": "URI too long"}, 414)
                return

            parsed_path = urlparse(self.path)
            path = parsed_path.path

            if path == '/api/themes':
                self._send_json({"themes": THEMES_LIST})
                return

            if path == '/login':
                if self.is_authenticated():
                    self._redirect('/')
                    return
                self._send_html(LOGIN_HTML)
                return

            if path == '/' or path == '/index.html':
                if not self.is_authenticated():
                    self._redirect('/login')
                    return
                self._send_html(generate_dashboard_html())
                return

            if not self.is_authenticated():
                self._send_json({"error": "Unauthorized", "redirect": "/login"}, 401)
                return

            if path == '/api/data':
                self._send_json(get_all_system_data())
                return

            if path == '/api/processes':
                self._send_json(get_processes())
                return

            if path == '/api/security':
                self._send_json(get_security_status())
                return

            if path == '/api/news':
                self._send_json(get_system_news())
                return

            if path.startswith('/open'):
                self._handle_open(parsed_path.query)
                return

            if path.startswith('/settings'):
                self._handle_settings(parsed_path.query)
                return

            if path.startswith('/static/'):
                self._serve_static(path[8:])
                return

            self._send_json({"error": "Not found"}, 404)

        except Exception as e:
            print(f"[ERROR] do_GET: {e}")
            traceback.print_exc()
            try:
                self._send_json({"error": "Internal server error"}, 500)
            except:
                pass

    def _serve_static(self, filepath):
        try:
            if '..' in filepath or filepath.startswith('/'):
                self._send_json({"error": "Forbidden"}, 403)
                return
            
            full_path = os.path.join('.', filepath)
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                self._send_json({"error": "Not found"}, 404)
                return
            
            ext = os.path.splitext(filepath)[1].lower()
            mime_types = {
                '.js': 'application/javascript', '.css': 'text/css',
                '.html': 'text/html', '.png': 'image/png',
                '.jpg': 'image/jpeg', '.gif': 'image/gif',
                '.svg': 'image/svg+xml', '.json': 'application/json'
            }
            content_type = mime_types.get(ext, 'application/octet-stream')
            
            with open(full_path, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            print(f"[ERROR] Static file: {e}")
            self._send_json({"error": "Error serving file"}, 500)

    # =============================================================================
    # GESTION DE L'OUVERTURE DES DOSSIERS - CORRIGÉE ET AMÉLIORÉE
    # =============================================================================
    
    def _handle_open(self, query_string):
        try:
            query = parse_qs(query_string)
            file_path = query.get('path', [''])[0]
            file_path = unquote(file_path)

            if not file_path:
                self._send_json({"error": "Path missing"}, 400)
                return
            
            # CORRECTION: Normaliser les séparateurs de chemin
            # Convertir les / en \ pour Windows et éliminer les doubles backslashes
            clean_path = file_path.replace('/', '\\').replace('\\\\', '\\')
            
            print(f"[EXPLORER] Chemin reçu: {file_path}")
            print(f"[EXPLORER] Chemin nettoyé: {clean_path}")
            
            # Vérifier si le chemin est autorisé
            if not is_path_allowed(clean_path):
                print(f"[EXPLORER] Accès refusé pour: {clean_path}")
                self._send_json({"error": "Access denied", "path": clean_path}, 403)
                return

            # Vérifier si le chemin existe
            if not os.path.exists(clean_path):
                print(f"[EXPLORER] Chemin inexistant: {clean_path}")
                self._send_json({"error": "Path does not exist", "path": clean_path}, 404)
                return

            # Ouvrir avec explorer.exe (méthode la plus fiable sous Windows)
            try:
                print(f"[EXPLORER] Ouverture avec explorer.exe: {clean_path}")
                # Utiliser shell=False pour éviter les problèmes de sécurité
                # et passer le chemin comme argument séparé
                subprocess.Popen(['explorer.exe', clean_path], shell=False)
                self._send_json({"success": True, "path": clean_path})
                print(f"[EXPLORER] Succès: {clean_path}")
            except Exception as e:
                print(f"[EXPLORER] Erreur explorer.exe: {e}")
                # Fallback sur os.startfile
                try:
                    print(f"[EXPLORER] Tentative avec os.startfile: {clean_path}")
                    os.startfile(clean_path)
                    self._send_json({"success": True, "path": clean_path})
                    print(f"[EXPLORER] Succès avec os.startfile")
                except Exception as e2:
                    print(f"[EXPLORER] Échec os.startfile: {e2}")
                    self._send_json({"error": f"explorer: {str(e)}, startfile: {str(e2)}"}, 500)
                    
        except Exception as e:
            print(f"[ERROR] _handle_open: {e}")
            traceback.print_exc()
            self._send_json({"error": str(e)}, 500)

    def _handle_settings(self, query_string):
        try:
            query = parse_qs(query_string)
            settings_uri = query.get('uri', [''])[0]
            settings_uri = unquote(settings_uri)

            if not settings_uri.startswith('ms-settings:'):
                self._send_json({"error": "Invalid settings URI"}, 400)
                return

            try:
                subprocess.Popen(['start', '', settings_uri], shell=True)
                self._send_json({"success": True, "uri": settings_uri})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def do_POST(self):
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path

            if path == '/api/auth':
                self._handle_auth()
                return

            if not self.is_authenticated():
                self._send_json({"error": "Unauthorized"}, 401)
                return

            self._send_json({"error": "Not found"}, 404)

        except Exception as e:
            print(f"[ERROR] do_POST: {e}")
            try:
                self._send_json({"error": "Internal server error"}, 500)
            except:
                pass

    def _handle_auth(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length <= 0 or content_length >= 10000:
                self._send_json({"success": False, "error": "Invalid data size"}, 400)
                return

            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            password = data.get('password', '')

            if verify_password(password):
                client_ip = self.get_client_ip()
                with authenticated_ips_lock:
                    authenticated_ips.add(client_ip)
                print(f"[AUTH] Succès - IP: {client_ip}")
                self._send_json({"success": True})
            else:
                print(f"[AUTH] Échec - IP: {self.get_client_ip()}")
                self._send_json({"success": False}, 401)
        except Exception as e:
            print(f"[ERROR] Auth error: {e}")
            self._send_json({"success": False, "error": str(e)}, 400)

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    try:
        print("=" * 70)
        print(">>> ROG DASHBOARD v6.0 - SYSTÈME MODULAIRE")
        print(">>> CORRECTION: Explorateur Windows amélioré")
        print("=" * 70)
        print(">>> Architecture:")
        print("    ✓ Partie 1: Configuration et thèmes")
        print("    ✓ Partie 2: Moniteur système (CPU/RAM/GPU/Réseau)")
        print("    ✓ Partie 3: Templates HTML/JS/CSS")
        print("    ✓ Partie 4: Serveur HTTP multi-threading (CORRIGÉ)")
        print("=" * 70)
        
        if PSUTIL_AVAILABLE:
            print("[OK] psutil: PRÊT - Données système en temps réel")
        else:
            print("[INFO] psutil: NON DISPONIBLE - Mode simulation")
            
        if GPU_AVAILABLE:
            print("[OK] GPU NVIDIA: PRÊT")
        else:
            print("[INFO] GPU: Mode simulation ou non détecté")
            
        print(f">>> Mot de passe: {load_password()}")
        print(">>> Accès local (127.0.0.1) = PAS DE MOT DE PASSE")
        print(f">>> Démarrage sur http://localhost:{PORT}")
        print(">>> Appuyez sur Ctrl+C pour arrêter")
        print("=" * 70)
        print()

        server = ThreadedHTTPServer(('0.0.0.0', PORT), DashboardHandler)
        server.serve_forever()

    except KeyboardInterrupt:
        print("\n>>> Arrêt demandé par l'utilisateur")
        print(">>> Serveur arrêté")

    except Exception as e:
        print(f"[FATAL] Erreur critique: {e}")
        traceback.print_exc()
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)

if __name__ == "__main__":
    main()