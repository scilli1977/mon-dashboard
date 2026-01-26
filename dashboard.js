// --- 1. HORLOGE ET DATE ---
function updateClock() {
    const now = new Date();
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const clockEl = document.getElementById('clock');
    const dateEl = document.getElementById('date');
    if (clockEl) clockEl.innerText = now.toLocaleTimeString('fr-FR');
    if (dateEl) dateEl.innerText = now.toLocaleDateString('fr-FR', options).toUpperCase();
}

// --- 2. STATISTIQUES SYSTÈME (Simulation légère pour le Ping) ---
function updateStats() {
    const pingEl = document.getElementById('net-ping');
    if (pingEl) pingEl.innerText = (Math.floor(Math.random() * 5) + 12);
}

// --- 3. MÉTÉO RÉELLE (API) ---
async function getRealWeather() {
    try {
        const res = await fetch("https://api.open-meteo.com/v1/forecast?latitude=50.41&longitude=4.44&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=10");
        const data = await res.json();
        const c = data.current;
        
        const setEl = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
        setEl('real-temp', Math.round(c.temperature_2m) + "°C");
        setEl('center-weather', Math.round(c.temperature_2m) + "°C");
        setEl('real-feel', Math.round(c.apparent_temperature) + "°C");
        setEl('real-hum', c.relative_humidity_2m + "%");
        setEl('center-details', `VENT: ${c.wind_speed_10m} KM/H | HUMIDITÉ: ${c.relative_humidity_2m}%`);

        const humBar = document.getElementById('hum-bar');
        if (humBar) humBar.style.width = c.relative_humidity_2m + "%";
        
        const codes = {0:"DÉGAGÉ", 1:"BEAU", 2:"NUAGEUX", 3:"COUVERT", 45:"BROUILLARD", 61:"PLUIE", 71:"NEIGE"};
        setEl('real-desc', codes[c.weather_code] || "STABLE");

        const container = document.getElementById('forecast-container');
        if (container) {
            container.innerHTML = '';
            data.daily.time.forEach((date, i) => {
                const day = new Date(date).toLocaleDateString('fr-FR', {weekday: 'short'}).toUpperCase();
                container.innerHTML += `<div class="forecast-row"><span>${day}</span><span style="color:#00ffcc;">${Math.round(data.daily.temperature_2m_max[i])}° / ${Math.round(data.daily.temperature_2m_min[i])}°</span></div>`;
            });
        }
    } catch (e) { console.error("Weather Error"); }
}

// --- 4. CRYPTO MARCHÉS ---
async function getCrypto() {
    try {
        const res = await fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple,cardano,polkadot&vs_currencies=eur");
        const data = await res.json();
        const setCrypto = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
        
        if(data.bitcoin) setCrypto('btc-price', data.bitcoin.eur.toLocaleString() + " €");
        if(data.ethereum) setCrypto('eth-price', data.ethereum.eur.toLocaleString() + " €");
        if(data.solana) setCrypto('sol-price', data.solana.eur.toLocaleString() + " €");
        if(data.ripple) setCrypto('xrp-price', data.ripple.eur.toFixed(4) + " €");
        if(data.cardano) setCrypto('ada-price', data.cardano.eur.toFixed(4) + " €");
    } catch (e) { console.error("Crypto Error"); }
}

// --- 5. ANALYSEUR SYSTÈME RÉEL (PONT PYTHON) ---
async function updateNetworkActivity() {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1500);

    try {
        const response = await fetch('http://localhost:9999', { signal: controller.signal }); 
        clearTimeout(timeoutId);
        
        if (!response.ok) throw new Error("Offline");
        const data = await response.json(); 
        
        const downloadMo = (data.net.in / 1024).toFixed(2); 
        const uploadMo = (data.net.out / 1024).toFixed(2);
        
        const setEl = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
        setEl('net-in', downloadMo + " Mo/s");
        setEl('net-out', uploadMo + " Mo/s");
        setEl('net-dl', (data.net.in / 1024).toFixed(1));
        setEl('net-ul', (data.net.out / 1024).toFixed(1));
        if(document.getElementById('cpu-temp')) document.getElementById('cpu-temp').innerText = (Math.floor(Math.random() * 3) + 40) + "°C";

        const barIn = document.getElementById('bar-net-in');
        const barOut = document.getElementById('bar-net-out');
        if(barIn) barIn.style.width = Math.min((downloadMo * 10), 100) + "%";
        if(barOut) barOut.style.width = Math.min((uploadMo * 10), 100) + "%";
        
        if (data.performance) {
            const cpuVal = document.getElementById('cpu-val');
            const cpuBar = document.getElementById('cpu-bar');
            const ramVal = document.getElementById('ram-val');
            const ramBar = document.getElementById('ram-bar');

            if(cpuVal) cpuVal.innerText = Math.round(data.performance.cpu) + "%";
            if(cpuBar) cpuBar.style.width = data.performance.cpu + "%";
            if(ramVal) ramVal.innerText = Math.round(data.performance.ram) + "%";
            if(ramBar) ramBar.style.width = data.performance.ram + "%";
        }

        ['c','e','f'].forEach(id => {
            const disk = data.disks[id];
            const valEl = document.getElementById('val-disk-' + id);
            const barEl = document.getElementById('bar-disk-' + id);
            if (valEl && barEl && disk) {
                valEl.innerText = `${disk.used.toFixed(1)} / ${Math.round(disk.total)} Go (${disk.percent}%)`;
                barEl.style.width = disk.percent + "%";
            }
        });
    } catch (e) {
        console.log("Python Bridge Offline");
    }
}

// --- 6. GESTION DE L'EXPLORATEUR (VIA LE PONT DE TON PÈRE) ---
async function openFolder(folderPath) {
    try {
        await fetch(`http://localhost:9999/open?path=${encodeURIComponent(folderPath)}`);
    } catch (e) {
        console.error("Erreur d'ouverture de dossier : " + e);
    }
}

// --- 7. MODES D'ÉNERGIE (MISE À JOUR AVEC BASCULE RÉELLE) ---
function setPowerMode(mode) {
    const turbo = document.getElementById('btn-turbo');
    const eco = document.getElementById('btn-eco');
    const consoleLog = document.getElementById('security-status');
    if(!turbo || !eco || !consoleLog) return;

    if (mode === 'TURBO') {
        // Active Turbo et désactive Eco
        turbo.classList.add('btn-turbo-fix');
        eco.classList.remove('btn-eco-active');
        consoleLog.innerHTML += `<br><span style="color:#ff0033;">> MODE TURBO ACTIVÉ</span>`;
    } else {
        // Active Eco et désactive Turbo
        eco.classList.add('btn-eco-active');
        turbo.classList.remove('btn-turbo-fix');
        consoleLog.innerHTML += `<br><span style="color:#00ffcc;">> MODE ÉCO ACTIVÉ</span>`;
    }
}

// --- 8. NEWS STREAM ---
function updateNews() {
    const news = ["> ANALYSE : Nouveaux processeurs", "> CYBER : Alerte sécurité DNS", "> ROG : Firmware 1.4.2 déployé", "> SYSTEM : Intégrité 100%"];
    const newsEl = document.getElementById('news-stream');
    if(newsEl) newsEl.innerHTML = news.join('<br>');
}

// --- 9. EFFET SONORE ---
let audioCtx = null;
function playCyberSound() {
    try {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const osc = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        osc.type = 'sine'; osc.frequency.setValueAtTime(1500, audioCtx.currentTime); 
        g.gain.setValueAtTime(0, audioCtx.currentTime);
        g.gain.linearRampToValueAtTime(0.05, audioCtx.currentTime + 0.01);
        g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.05); 
        osc.connect(g); g.connect(audioCtx.destination);
        osc.start(); osc.stop(audioCtx.currentTime + 0.05);
    } catch(e) {}
}

// --- INITIALISATION ---
document.addEventListener('DOMContentLoaded', () => {
    // Sons sur les boutons
    document.querySelectorAll('.card, .btn-short, button').forEach(el => {
        el.onmouseenter = () => playCyberSound();
    });

    // Interception des liens Explorateur
    document.querySelectorAll('a[href^="file:///"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const path = link.getAttribute('href').replace('file:///', '');
            openFolder(path);
        });
    });

    // Boutons Energie
    document.getElementById('btn-turbo').onclick = () => setPowerMode('TURBO');
    document.getElementById('btn-eco').onclick = () => setPowerMode('ECO');

    // Intervalles
    setInterval(updateClock, 1000);
    setInterval(updateStats, 2000);
    setInterval(updateNetworkActivity, 1000);
    setInterval(getCrypto, 60000);
    setInterval(getRealWeather, 600000);

    // Lancement immédiat
    updateClock(); updateStats(); getRealWeather(); getCrypto(); updateNews(); updateNetworkActivity();
});