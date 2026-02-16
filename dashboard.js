// --- CONFIGURATION ---
const CONFIG = {
    API_URL: 'http://localhost:9999',
    REFRESH_RATE: {
        SYSTEM: 2000,
        CRYPTO: 60000,
        WEATHER: 600000
    },
    CACHE_DURATION: 300000,
    BACKEND_TIMEOUT: 3000,
    OFFLINE_MODE: false
};

// --- CACHE LOCAL ---
const Cache = {
    get: (key) => {
        const item = localStorage.getItem(`rog_${key}`);
        if (!item) return null;
        const { value, timestamp } = JSON.parse(item);
        if (Date.now() - timestamp > CONFIG.CACHE_DURATION) {
            localStorage.removeItem(`rog_${key}`);
            return null;
        }
        return value;
    },
    set: (key, value) => {
        localStorage.setItem(`rog_${key}`, JSON.stringify({
            value, timestamp: Date.now()
        }));
    }
};

// --- ÉTAT SYSTÈME ---
let backendOnline = false;
let backendRetryCount = 0;
let simulatedDataInterval = null;

// ==========================================
// GESTION DES THÈMES
// ==========================================

const ThemeManager = {
    currentTheme: localStorage.getItem('rog_theme') || 'dark',

    themes: ['dark', 'light', 'red', 'purple', 'orange', 'ice', 'green', 'pink', 'yellow', 'lime', 'teal', 'magenta', 'gold', 'blood', 'ocean', 'forest', 'midnight', 'cherry', 'cyber', 'matrix', 'sunset'],

    init() {
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
        this.updateActiveButton();
    },

    applyTheme(themeName) {
        document.documentElement.setAttribute('data-theme', themeName);
        this.currentTheme = themeName;
        localStorage.setItem('rog_theme', themeName);
        this.updateActiveButton();
        this.showThemeNotification(themeName);
    },

    showThemeNotification(themeName) {
        const notification = document.getElementById('theme-notification');
        if (!notification) return;

        const labels = {
            dark: 'ROG Cyberpunk', light: 'Mode Jour', red: 'Red Gaming', purple: 'Purple Neon',
            orange: 'Amber', ice: 'Ice Cold', green: 'Matrix Green', pink: 'Hot Pink',
            yellow: 'Golden Sun', lime: 'Toxic Lime', teal: 'Deep Teal', magenta: 'Neon Magenta',
            gold: 'Royal Gold', blood: 'Blood Red', ocean: 'Deep Ocean', forest: 'Forest Green',
            midnight: 'Midnight Blue', cherry: 'Cherry Blossom', cyber: 'Cyber Purple',
            matrix: 'Classic Matrix', sunset: 'Sunset Orange'
        };

        notification.textContent = `Thème: ${labels[themeName] || themeName}`;
        notification.classList.add('show');
        setTimeout(() => notification.classList.remove('show'), 2000);
    },

    setupEventListeners() {
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const theme = e.target.dataset.theme;
                this.applyTheme(theme);
                playCyberSound();
            });
        });

        const modeToggle = document.getElementById('mode-toggle');
        if (modeToggle) {
            modeToggle.addEventListener('click', () => {
                const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
                this.applyTheme(newTheme);
                playCyberSound();
            });
        }
    },

    updateActiveButton() {
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === this.currentTheme);
        });

        const modeIcon = document.getElementById('mode-icon');
        if (modeIcon) {
            modeIcon.textContent = this.currentTheme === 'light' ? '☀️' : '🌙';
        }
    }
};

// ==========================================
// DONNÉES SIMULÉES (MODE OFFLINE)
// ==========================================

const OfflineData = {
    generate() {
        const now = new Date();
        return {
            status: "offline",
            timestamp: now.getTime(),
            performance: {
                cpu: Math.random() * 30 + 10,
                ram: Math.random() * 40 + 30,
                cpu_temp: 40 + Math.random() * 15
            },
            disks: {
                c: { total: 930.5, used: 733.5, free: 197.0, percent: 78 },
                e: { total: 931.5, used: 701.6, free: 229.9, percent: 75 },
                f: { total: 931.5, used: 32.3, free: 899.2, percent: 3 }
            },
            net: {
                in: Math.random() * 5,
                out: Math.random() * 2,
                history: {
                    in: Array(60).fill(0).map(() => Math.random() * 5),
                    out: Array(60).fill(0).map(() => Math.random() * 2)
                }
            },
            gpu: null,
            processes: [
                { name: "System Idle", cpu: 94.0 },
                { name: "firefox.exe", cpu: 2.4 },
                { name: "explorer.exe", cpu: 0.8 },
                { name: "python.exe", cpu: 0.5 },
                { name: "discord.exe", cpu: 0.3 }
            ],
            security: {
                firewall: "ACTIF - Windows Defender",
                ports: "SCAN: AUCUNE MENACE",
                vpn: "DÉCONNECTÉ",
                encryption: "AES-256-GCM"
            },
            news: [
                "[SYS] Mode offline - Données simulées",
                "[NET] Connexion au serveur perdue",
                "[GPU] Surveillance désactivée",
                "[SEC] Sécurité maintenue",
                "[INF] Utilisation données locales"
            ]
        };
    },

    startSimulation() {
        if (simulatedDataInterval) return;
        
        console.log("[OFFLINE] Démarrage simulation données");
        
        // Mise à jour immédiate
        renderSystemData(this.generate());
        
        // Mises à jour périodiques
        simulatedDataInterval = setInterval(() => {
            renderSystemData(this.generate());
        }, CONFIG.REFRESH_RATE.SYSTEM);
    },

    stopSimulation() {
        if (simulatedDataInterval) {
            clearInterval(simulatedDataInterval);
            simulatedDataInterval = null;
            console.log("[ONLINE] Arrêt simulation données");
        }
    }
};

// ==========================================
// FONCTIONS DE RENDU
// ==========================================

function updateClock() {
    const now = new Date();
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const clockEl = document.getElementById('clock');
    const dateEl = document.getElementById('date');
    
    if (clockEl) clockEl.innerText = now.toLocaleTimeString('fr-FR');
    if (dateEl) dateEl.innerText = now.toLocaleDateString('fr-FR', options).toUpperCase();
}

function renderWeather(data) {
    if (!data) return;
    
    const c = data.current || data;
    const setEl = (id, val) => { 
        const el = document.getElementById(id); 
        if(el) el.innerText = val; 
    };

    setEl('real-temp', Math.round(c.temperature_2m || c.temp || 20) + "°C");
    setEl('center-weather', Math.round(c.temperature_2m || c.temp || 20) + "°C");
    setEl('real-feel', Math.round(c.apparent_temperature || c.feels_like || 20) + "°C");
    setEl('real-hum', (c.relative_humidity_2m || c.humidity || 50) + "%");
    setEl('center-details', `VENT: ${c.wind_speed_10m || c.wind || 10} KM/H | HUMIDITÉ: ${c.relative_humidity_2m || c.humidity || 50}%`);

    const humBar = document.getElementById('hum-bar');
    if (humBar) humBar.style.width = (c.relative_humidity_2m || c.humidity || 50) + "%";

    const codes = {0:"DÉGAGÉ", 1:"BEAU", 2:"NUAGEUX", 3:"COUVERT", 45:"BROUILLARD", 61:"PLUIE", 71:"NEIGE"};
    setEl('real-desc', codes[c.weather_code] || "STABLE");

    const container = document.getElementById('forecast-container');
    if (container && data.daily) {
        container.innerHTML = '';
        data.daily.time.forEach((date, i) => {
            const day = new Date(date).toLocaleDateString('fr-FR', {weekday: 'short'}).toUpperCase();
            container.innerHTML += `<div class="forecast-row"><span>${day}</span><span style="color:var(--accent-primary);">${Math.round(data.daily.temperature_2m_max[i])}° / ${Math.round(data.daily.temperature_2m_min[i])}°</span></div>`;
        });
    }
}

function renderCrypto(data) {
    const setCrypto = (id, val) => { 
        const el = document.getElementById(id); 
        if(el) el.innerText = val; 
    };

    if(data.bitcoin) setCrypto('btc-price', data.bitcoin.eur.toLocaleString() + " €");
    if(data.ethereum) setCrypto('eth-price', data.ethereum.eur.toLocaleString() + " €");
    if(data.solana) setCrypto('sol-price', data.solana.eur.toLocaleString() + " €");
    if(data.ripple) setCrypto('xrp-price', data.ripple.eur.toFixed(4) + " €");
    if(data.cardano) setCrypto('ada-price', data.cardano.eur.toFixed(4) + " €");
}

function renderSystemData(data) {
    console.log("Données reçues:", data);

    // --- RÉSEAU ---
    if (data.net) {
        const downloadMo = (data.net.in / 1024).toFixed(2);
        const uploadMo = (data.net.out / 1024).toFixed(2);

        const setEl = (id, val) => { 
            const el = document.getElementById(id); 
            if(el) el.innerText = val;
        };

        setEl('net-in', downloadMo + " Mo/s");
        setEl('net-out', uploadMo + " Mo/s");
        setEl('net-dl', (data.net.in / 1024).toFixed(1));
        setEl('net-ul', (data.net.out / 1024).toFixed(1));

        const pingEl = document.getElementById('net-ping');
        if(pingEl) pingEl.innerText = Math.floor(Math.random() * 5) + 12;

        const barIn = document.getElementById('bar-net-in');
        const barOut = document.getElementById('bar-net-out');
        if(barIn) barIn.style.width = Math.min((data.net.in / 1024 * 10), 100) + "%";
        if(barOut) barOut.style.width = Math.min((data.net.out / 1024 * 10), 100) + "%";

        if (data.net.history) {
            renderNetGraph(data.net.history);
        }
    }

    // --- CPU ---
    if (data.performance) {
        const cpuVal = document.getElementById('cpu-val');
        const cpuBar = document.getElementById('cpu-bar');
        const cpuTemp = document.getElementById('cpu-temp');

        if(cpuVal) cpuVal.innerText = Math.round(data.performance.cpu) + "%";
        if(cpuBar) cpuBar.style.width = data.performance.cpu + "%";
        if(cpuTemp) cpuTemp.innerText = (Math.floor(data.performance.cpu_temp || 40)) + "°C";

        const ramVal = document.getElementById('ram-val');
        const ramBar = document.getElementById('ram-bar');

        if(ramVal) ramVal.innerText = Math.round(data.performance.ram) + "%";
        if(ramBar) ramBar.style.width = data.performance.ram + "%";
    }

    // --- DISQUES ---
    if (data.disks) {
        if (data.disks.c) {
            const valDiskC = document.getElementById('val-disk-c');
            const barDiskC = document.getElementById('bar-disk-c');
            if(valDiskC) valDiskC.innerText = `${data.disks.c.used.toFixed(1)} / ${Math.round(data.disks.c.total)} Go (${data.disks.c.percent}%)`;
            if(barDiskC) barDiskC.style.width = data.disks.c.percent + "%";
        }

        if (data.disks.e) {
            const valDiskE = document.getElementById('val-disk-e');
            const barDiskE = document.getElementById('bar-disk-e');
            if(valDiskE) valDiskE.innerText = `${data.disks.e.used.toFixed(1)} / ${Math.round(data.disks.e.total)} Go (${data.disks.e.percent}%)`;
            if(barDiskE) barDiskE.style.width = data.disks.e.percent + "%";
        }

        if (data.disks.f) {
            const valDiskF = document.getElementById('val-disk-f');
            const barDiskF = document.getElementById('bar-disk-f');
            if(valDiskF) valDiskF.innerText = `${data.disks.f.used.toFixed(1)} / ${Math.round(data.disks.f.total)} Go (${data.disks.f.percent}%)`;
            if(barDiskF) barDiskF.style.width = data.disks.f.percent + "%";
        }
    }

    // --- GPU ---
    if (data.gpu) {
        renderGPU(data.gpu);
    } else {
        const gpuWidget = document.getElementById('gpu-widget');
        if(gpuWidget) gpuWidget.style.display = 'none';
    }

    // --- PROCESSUS ---
    if (data.processes) {
        updateProcessList(data.processes);
    }

    // --- SÉCURITÉ ---
    if (data.security) {
        updateSecurityStatus(data.security);
    }

    // --- NEWS ---
    if (data.news) {
        updateNews(data.news);
    }
}

function renderGPU(gpu) {
    const gpuWidget = document.getElementById('gpu-widget');
    if(gpuWidget) gpuWidget.style.display = 'block';

    const gpuName = gpu.name ? (gpu.name.length > 25 ? gpu.name.substring(0, 25) + '...' : gpu.name) : 'GPU';
    const gpuNameEl = document.getElementById('gpu-name');
    if(gpuNameEl) gpuNameEl.innerText = gpuName;

    const gpuLoadEl = document.getElementById('gpu-load');
    const gpuBar = document.getElementById('gpu-bar');
    if(gpuLoadEl) gpuLoadEl.innerText = gpu.load + "%";
    if(gpuBar) gpuBar.style.width = gpu.load + "%";

    const gpuTempEl = document.querySelector('#gpu-widget #gpu-temp');
    if(gpuTempEl && gpu.temp !== undefined) {
        gpuTempEl.innerText = gpu.temp + "°C";
    }

    const vramUsed = (gpu.memory_used / 1024).toFixed(1);
    const vramTotal = (gpu.memory_total / 1024).toFixed(1);
    const gpuVramEl = document.getElementById('gpu-vram');
    const vramBar = document.getElementById('gpu-vram-bar');
    if(gpuVramEl) gpuVramEl.innerText = `${vramUsed} / ${vramTotal} Go`;
    if(vramBar) vramBar.style.width = gpu.memory_percent + "%";
}

function renderNetGraph(history) {
    const canvas = document.getElementById('net-graph-canvas');
    if(!canvas) return;

    const container = canvas.parentElement;
    if (container) {
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
    }

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fillRect(0, 0, width, height);

    const maxVal = Math.max(...history.in, ...history.out, 1);

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for(let i = 1; i < 4; i++) {
        const y = (height / 4) * i;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }

    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-primary').trim() || '#00ffcc';
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = 2;
    ctx.beginPath();
    history.in.forEach((val, i) => {
        const x = (width / (history.in.length - 1)) * i;
        const y = height - ((val / maxVal) * height * 0.9);
        if(i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-secondary').trim() || '#00ccff';
    ctx.strokeStyle = secondaryColor;
    ctx.beginPath();
    history.out.forEach((val, i) => {
        const x = (width / (history.out.length - 1)) * i;
        const y = height - ((val / maxVal) * height * 0.9);
        if(i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.font = '9px Orbitron';
    ctx.fillStyle = primaryColor;
    ctx.fillText('▼ DL', 5, 12);
    ctx.fillStyle = secondaryColor;
    ctx.fillText('▲ UL', 35, 12);
}

function updateProcessList(processes) {
    const processEl = document.getElementById('process-list');
    if (!processEl || !Array.isArray(processes)) return;

    if (processes.length === 0) {
        processEl.innerHTML = '<span style="color: var(--text-muted);">Aucun processus actif détecté</span>';
        return;
    }

    processEl.innerHTML = processes.map(proc => {
        const name = proc.name.length > 15 ? proc.name.substring(0, 15) + '...' : proc.name;
        const colorClass = proc.cpu > 50 ? 'text-red' : (proc.cpu > 20 ? 'status-warning' : 'status-ok');
        return `${name} <span class="${colorClass}" style="float:right;">${proc.cpu.toFixed(1)}%</span>`;
    }).join('<br>');
}

function updateSecurityStatus(security) {
    const consoleEl = document.getElementById('security-status');
    if (!consoleEl) return;

    consoleEl.innerHTML = `
        <span style="color: var(--accent-primary);">> FIREWALL :</span> ${security.firewall}<br>
        <span style="color: var(--accent-primary);">> PORTS :</span> ${security.ports}<br>
        <span style="color: var(--accent-primary);">> VPN :</span> ${security.vpn}<br>
        <span style="color: var(--accent-primary);">> ENCRYPTION :</span> ${security.encryption}
    `;
}

function updateNews(newsItems) {
    const newsEl = document.getElementById('news-stream');
    if (!newsEl || !Array.isArray(newsItems)) return;

    newsEl.innerHTML = newsItems.map(item => `> ${item}`).join('<br>');
}

function updateBackendStatus(isOnline, text) {
    const dotEl = document.getElementById('backend-dot');
    const textEl = document.getElementById('backend-text');

    if (dotEl) {
        dotEl.className = isOnline ? 'status-dot online' : 'status-dot offline';
    }

    if (textEl) {
        textEl.textContent = text || (isOnline ? 'ONLINE' : 'OFFLINE');
        textEl.style.color = isOnline ? '#00ff00' : '#ff0033';
    }

    // Gestion du mode offline
    if (isOnline) {
        OfflineData.stopSimulation();
        CONFIG.OFFLINE_MODE = false;
    } else {
        OfflineData.startSimulation();
        CONFIG.OFFLINE_MODE = true;
    }
}

// ==========================================
// COMMUNICATION SERVEUR
// ==========================================

async function fetchWithTimeout(url, options = {}, timeout = CONFIG.BACKEND_TIMEOUT) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

async function updateNetworkActivity() {
    try {
        const response = await fetchWithTimeout(`${CONFIG.API_URL}/api/data`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!backendOnline) {
            backendOnline = true;
            backendRetryCount = 0;
            updateBackendStatus(true, "ONLINE");
            document.body.classList.remove('backend-offline');
            showToast("Connexion au système établie", "success");
        }

        renderSystemData(data);
        Cache.set('system', data);

    } catch (e) {
        console.error("Network Activity Error:", e);

        if (backendOnline) {
            backendOnline = false;
            backendRetryCount++;
            updateBackendStatus(false, "OFFLINE");
            document.body.classList.add('backend-offline');

            if (backendRetryCount <= 3) {
                showToast("Connexion au système perdue - Mode offline", "error");
            }
        }

        // Utiliser les données en cache si disponibles
        const cached = Cache.get('system');
        if (cached) {
            renderSystemData(cached);
        }
    }
}

async function getRealWeather() {
    const cached = Cache.get('weather');
    if (cached) renderWeather(cached);

    try {
        const res = await fetch("https://api.open-meteo.com/v1/forecast?latitude=50.41&longitude=4.44&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=10");
        const data = await res.json();
        Cache.set('weather', data);
        renderWeather(data);
    } catch (e) { 
        console.error("Weather Error", e);
        // Données météo simulées en fallback
        renderWeather({
            current: { temperature_2m: 22, apparent_temperature: 21, relative_humidity_2m: 65, weather_code: 1, wind_speed_10m: 12 },
            daily: { time: Array(10).fill(new Date().toISOString()), temperature_2m_max: Array(10).fill(25), temperature_2m_min: Array(10).fill(15) }
        });
    }
}

async function getCrypto() {
    const cached = Cache.get('crypto');
    if (cached) renderCrypto(cached);

    try {
        const res = await fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple,cardano&vs_currencies=eur");
        const data = await res.json();
        Cache.set('crypto', data);
        renderCrypto(data);
    } catch (e) { 
        console.error("Crypto Error", e);
    }
}

// ==========================================
// GESTION SYSTÈME ET EXPLORATEUR - CORRIGÉ
// ==========================================

function openWindowsSettings(settingsUri) {
    console.log("Ouverture paramètres Windows:", settingsUri);

    try {
        // Méthode iframe cachée
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.style.width = '0';
        iframe.style.height = '0';
        iframe.style.border = 'none';
        iframe.style.position = 'absolute';
        iframe.style.top = '-1000px';
        iframe.src = settingsUri;

        document.body.appendChild(iframe);

        setTimeout(() => {
            if (iframe.parentNode) {
                document.body.removeChild(iframe);
            }
        }, 3000);

        showToast(`Ouverture: ${settingsUri.replace('ms-settings:', '')}`, "success");

    } catch (e) {
        console.error("Erreur ouverture paramètres:", e);
        showToast(`Erreur: Impossible d'ouvrir ${settingsUri}`, "error");
    }
}

const folderRequestCache = new Map();
const FOLDER_CACHE_DURATION = 5000;

// ==========================================
// FONCTION EXPLORATEUR - CORRIGÉE ET OPTIMISÉE
// ==========================================

async function openFolder(folderPath) {
    const now = Date.now();
    const cached = folderRequestCache.get(folderPath);
    if (cached && (now - cached.time) < FOLDER_CACHE_DURATION) {
        console.log("[CACHE] Ouverture récente, ignorée:", folderPath);
        return;
    }

    folderRequestCache.set(folderPath, { time: now });

    try {
        console.log("Ouverture dossier:", folderPath);

        // CORRECTION: Normaliser le chemin - convertir / en \ pour Windows
        let cleanPath = folderPath.replace(/\//g, '\\');
        
        // Supprimer les préfixes file:// ou file:\\ si présents
        if (cleanPath.startsWith('file:\\\\\\\\')) {
            cleanPath = cleanPath.substring(8);
        } else if (cleanPath.startsWith('file://')) {
            cleanPath = cleanPath.substring(7);
        }
        
        // Éliminer les backslashes multiples
        cleanPath = cleanPath.replace(/\\\\+/g, '\\');

        // Vérifier que le chemin n'est pas vide
        if (!cleanPath || cleanPath.length < 2) {
            showToast("Chemin invalide", "error");
            return;
        }

        // Encoder pour l'URL
        const encodedPath = encodeURIComponent(cleanPath);
        const url = `${CONFIG.API_URL}/open?path=${encodedPath}`;

        console.log("URL envoyée au serveur:", url);

        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });

        if (!response.ok) {
            if (response.status === 414) {
                throw new Error("URI trop longue - chemin trop long");
            }
            throw new Error(`Erreur serveur: ${response.status}`);
        }

        const data = await response.json();

        if (data.success || data.ok) {
            const folderName = cleanPath.split('\\').pop() || cleanPath;
            showToast(`Ouverture: ${folderName}`, "success");
        } else {
            throw new Error(data.error || "Réponse invalide du serveur");
        }

    } catch (e) {
        console.error("Erreur ouverture dossier:", e);
        showToast(`Impossible d'ouvrir: ${e.message}`, "error");
    }
}

// ==========================================
// UTILITAIRES UI
// ==========================================

function showToast(message, type = 'info') {
    const existingToasts = document.querySelectorAll('.rog-toast');
    if (existingToasts.length >= 3) {
        existingToasts[0].remove();
    }

    const toast = document.createElement('div');
    toast.className = 'rog-toast';
    const colors = {
        success: '#00ffcc',
        error: '#ff0033',
        warning: '#ff8c00',
        info: '#00ccff'
    };

    toast.style.cssText = `
        position: fixed;
        bottom: ${20 + (existingToasts.length * 60)}px;
        right: 20px;
        background: rgba(0,0,0,0.9);
        border: 1px solid ${colors[type]};
        color: ${colors[type]};
        padding: 12px 20px;
        border-radius: 4px;
        font-family: 'Orbitron', sans-serif;
        font-size: 11px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
        box-shadow: 0 0 20px ${colors[type]}40;
        max-width: 300px;
        word-wrap: break-word;
    `;
    toast.innerText = `> ${message}`;

    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function setPowerMode(mode) {
    const turbo = document.getElementById('btn-turbo');
    const eco = document.getElementById('btn-eco');
    const consoleLog = document.getElementById('security-status');
    if(!turbo || !eco || !consoleLog) return;

    if (mode === 'TURBO') {
        turbo.classList.add('btn-turbo-fix');
        eco.classList.remove('btn-eco-active');
        consoleLog.innerHTML += `<br><span style="color:#ff0033;">> MODE TURBO ACTIVÉ</span>`;
        showToast("Mode Turbo activé", "success");
    } else {
        eco.classList.add('btn-eco-active');
        turbo.classList.remove('btn-turbo-fix');
        consoleLog.innerHTML += `<br><span style="color:#00ffcc;">> MODE ÉCO ACTIVÉ</span>`;
        showToast("Mode Éco activé", "success");
    }
}

let audioCtx = null;
function playCyberSound() {
    try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1500, audioCtx.currentTime);
        g.gain.setValueAtTime(0, audioCtx.currentTime);
        g.gain.linearRampToValueAtTime(0.05, audioCtx.currentTime + 0.01);
        g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.05);
        osc.connect(g);
        g.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.05);
    } catch(e) {}
}

// ==========================================
// STYLES DYNAMIQUES
// ==========================================

const offlineStyles = document.createElement('style');
offlineStyles.textContent = `
    .backend-offline .widget-box {
        opacity: 0.7;
        border-color: #ff0033 !important;
    }
    .backend-offline #cpu-val, .backend-offline #ram-val {
        color: #ff0033 !important;
    }
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 1; }
    }
    .status-warning {
        color: #ff8c00 !important;
        text-shadow: 0 0 5px #ff8c00;
    }
`;
document.head.appendChild(offlineStyles);

// ==========================================
// INITIALISATION
// ==========================================

let intervals = [];

function setTrackedInterval(fn, delay) {
    const id = setInterval(fn, delay);
    intervals.push(id);
    return id;
}

window.addEventListener('beforeunload', () => {
    intervals.forEach(clearInterval);
    OfflineData.stopSimulation();
});

document.addEventListener('DOMContentLoaded', () => {
    console.log("Dashboard ROG v6.0 chargé - Mode Offline supporté");

    ThemeManager.init();

    // ==========================================
    // GESTION DES LIENS - CORRIGÉE
    // ==========================================
    
    let lastClickTime = 0;
    const CLICK_DEBOUNCE = 500;

    // Fonction pour détecter si c'est un chemin Windows local
    function isWindowsPath(href) {
        if (!href) return false;
        // Détecte C:/ ou C:\ ou file://
        if (/^[a-zA-Z]:[\\\/]/.test(href)) return true;
        if (href.startsWith('file:///')) return true;
        if (href.startsWith('file:\\\\\\\\')) return true;
        return false;
    }

    // Gestionnaire global des clics
    document.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');

        // Gestion des liens Windows (Explorateur)
        if (isWindowsPath(href)) {
            const now = Date.now();
            if (now - lastClickTime < CLICK_DEBOUNCE) {
                console.log("[DEBOUNCE] Clic ignoré");
                e.preventDefault();
                e.stopPropagation();
                return;
            }
            lastClickTime = now;

            e.preventDefault();
            e.stopPropagation();

            console.log("Clic Explorateur détecté:", href);
            openFolder(href);
            return;
        }

        // Gestion des liens ms-settings (Paramètres Windows)
        if (href && href.startsWith('ms-settings:')) {
            e.preventDefault();
            e.stopPropagation();
            console.log("Clic Paramètres Windows détecté:", href);
            openWindowsSettings(href);
            return;
        }
    });

    // Sons interactifs
    document.querySelectorAll('.card, .btn-short, button, .theme-btn').forEach(el => {
        el.onmouseenter = () => playCyberSound();
    });

    // Boutons Énergie
    const btnTurbo = document.getElementById('btn-turbo');
    const btnEco = document.getElementById('btn-eco');
    if(btnTurbo) btnTurbo.onclick = () => setPowerMode('TURBO');
    if(btnEco) btnEco.onclick = () => setPowerMode('ECO');

    // Démarrage des mises à jour
    updateClock();
    getRealWeather();
    getCrypto();
    updateNetworkActivity();

    setTrackedInterval(updateClock, 1000);
    setTrackedInterval(updateNetworkActivity, CONFIG.REFRESH_RATE.SYSTEM);
    setTrackedInterval(getCrypto, CONFIG.REFRESH_RATE.CRYPTO);
    setTrackedInterval(getRealWeather, CONFIG.REFRESH_RATE.WEATHER);

    console.log("Dashboard initialisé avec succès - Backend:", CONFIG.API_URL);
});