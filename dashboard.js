// --- 1. HORLOGE ET DATE ---
    function updateClock() {
        const now = new Date();
        const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
        document.getElementById('clock').innerText = now.toLocaleTimeString('fr-FR');
        document.getElementById('date').innerText = now.toLocaleDateString('fr-FR', options).toUpperCase();
    }

    // --- 2. STATISTIQUES SYSTÈME (Simulation Température/Ping uniquement) ---
    function updateStats() {
        const temp = Math.floor(Math.random() * 5) + 42;
        document.getElementById('cpu-temp').innerText = temp + "°C";
        document.getElementById('net-ping').innerText = Math.floor(Math.random() * 5) + 10;
    }

    // --- 3. MÉTÉO RÉELLE (API) ---
    async function getRealWeather() {
        try {
            const res = await fetch("https://api.open-meteo.com/v1/forecast?latitude=50.41&longitude=4.44&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=10");
            const data = await res.json();
            const c = data.current;
            
            document.getElementById('real-temp').innerText = Math.round(c.temperature_2m) + "°C";
            document.getElementById('center-weather').innerText = Math.round(c.temperature_2m) + "°C";
            document.getElementById('real-feel').innerText = Math.round(c.apparent_temperature) + "°C";
            document.getElementById('real-hum').innerText = c.relative_humidity_2m + "%";
            document.getElementById('hum-bar').style.width = c.relative_humidity_2m + "%";
            document.getElementById('center-details').innerText = `VENT: ${c.wind_speed_10m} KM/H | HUMIDITÉ: ${c.relative_humidity_2m}%`;
            
            const codes = {0:"DÉGAGÉ", 1:"BEAU", 2:"NUAGEUX", 3:"COUVERT", 45:"BROUILLARD", 61:"PLUIE", 71:"NEIGE"};
            document.getElementById('real-desc').innerText = codes[c.weather_code] || "STABLE";

            const container = document.getElementById('forecast-container');
            container.innerHTML = '';
            data.daily.time.forEach((date, i) => {
                const day = new Date(date).toLocaleDateString('fr-FR', {weekday: 'short'}).toUpperCase();
                container.innerHTML += `<div class="forecast-row"><span>${day}</span><span style="color:#00ffcc;">${Math.round(data.daily.temperature_2m_max[i])}° / ${Math.round(data.daily.temperature_2m_min[i])}°</span></div>`;
            });
        } catch (e) { console.error("Weather Error"); }
    }

    // --- 4. CRYPTO MARCHÉS ---
    async function getCrypto() {
        try {
            const res = await fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,ripple,cardano,polkadot&vs_currencies=eur");
            const data = await res.json();
            
            document.getElementById('btc-price').innerText = data.bitcoin.eur.toLocaleString() + " €";
            document.getElementById('eth-price').innerText = data.ethereum.eur.toLocaleString() + " €";
            document.getElementById('sol-price').innerText = data.solana.eur.toLocaleString() + " €";
            document.getElementById('xrp-price').innerText = data.ripple.eur.toFixed(4) + " €";
            document.getElementById('ada-price').innerText = data.cardano.eur.toFixed(4) + " €";
        } catch (e) { console.error("Crypto Error"); }
    }

    // --- 5. ANALYSEUR SYSTÈME RÉEL (PONT PYTHON) ---
    async function updateNetworkActivity() {
        try {
            const response = await fetch('http://localhost:9999'); 
            if (!response.ok) throw new Error("Offline");
            const data = await response.json(); 
            
            const downloadMo = (data.net.in / 1024).toFixed(2); 
            const uploadMo = (data.net.out / 1024).toFixed(2);
            
            if(document.getElementById('net-in')) document.getElementById('net-in').innerText = downloadMo + " Mo/s";
            if(document.getElementById('net-out')) document.getElementById('net-out').innerText = uploadMo + " Mo/s";
            if(document.getElementById('net-dl')) document.getElementById('net-dl').innerText = (data.net.in / 1024).toFixed(1);
            if(document.getElementById('net-ul')) document.getElementById('net-ul').innerText = (data.net.out / 1024).toFixed(1);
            if(document.getElementById('bar-net-in')) document.getElementById('bar-net-in').style.width = Math.min((downloadMo * 10), 100) + "%";
            if(document.getElementById('bar-net-out')) document.getElementById('bar-net-out').style.width = Math.min((uploadMo * 10), 100) + "%";
            
            if (data.performance) {
                const cpuVal = document.getElementById('cpu-val');
                const cpuBar = document.getElementById('cpu-bar');
                const ramVal = document.getElementById('ram-val');
                const ramBar = document.getElementById('ram-bar');
                if(cpuVal) cpuVal.innerText = data.performance.cpu + "%";
                if(cpuBar) cpuBar.style.width = data.performance.cpu + "%";
                if(ramVal) ramVal.innerText = data.performance.ram + "%";
                if(ramBar) ramBar.style.width = data.performance.ram + "%";
                if (data.performance.cpu > 90 && cpuVal) cpuVal.classList.add('text-red');
                else if(cpuVal) cpuVal.classList.remove('text-red');
            }

            const disks = [{ id: 'c', info: data.disks.c }, { id: 'e', info: data.disks.e }, { id: 'f', info: data.disks.f }];
            disks.forEach(disk => {
                const valEl = document.getElementById('val-disk-' + disk.id);
                const barEl = document.getElementById('bar-disk-' + disk.id);
                if (valEl && barEl && disk.info) {
                    valEl.innerText = disk.info.used.toFixed(1) + " / " + Math.round(disk.info.total) + " Go (" + disk.info.percent + "%)";
                    barEl.style.width = disk.info.percent + "%";
                    if (disk.info.percent >= 90) { barEl.classList.add('bar-fill-red'); valEl.classList.add('text-red'); }
                    else { barEl.classList.remove('bar-fill-red'); valEl.classList.remove('text-red'); }
                }
            });
        } catch (e) {
            console.log("Erreur Pont Python : Serveur non lancé");
            if(document.getElementById('net-in')) document.getElementById('net-in').innerText = "OFFLINE";
            if(document.getElementById('net-out')) document.getElementById('net-out').innerText = "OFFLINE";
            if(document.getElementById('cpu-val')) document.getElementById('cpu-val').innerText = "OFFLINE";
            if(document.getElementById('ram-val')) document.getElementById('ram-val').innerText = "OFFLINE";
            ['c','e','f'].forEach(id => { if(document.getElementById('val-disk-' + id)) document.getElementById('val-disk-' + id).innerText = "OFFLINE"; });
        }
    }

    // --- 6. FONCTION D'OUVERTURE DE DOSSIER (VIA PYTHON) ---
    function openFolder(path) {
        console.log("Demande d'ouverture locale : " + path);
        fetch(`http://localhost:9999/open?path=${encodeURIComponent(path)}`)
            .catch(err => console.error("Erreur pont lors de l'ouverture :", err));
    }

    // --- 7. MODES D'ÉNERGIE ---
    function setPowerMode(mode) {
        const turbo = document.getElementById('btn-turbo');
        const eco = document.getElementById('btn-eco');
        const consoleLog = document.querySelector('.sidebar-right .console-box');
        if (mode === 'TURBO') {
            turbo.classList.add('btn-turbo-fix');
            eco.classList.remove('btn-turbo-fix');
            consoleLog.innerHTML += `<br>> Mode TURBO activé : Fréquences max.`;
        } else {
            eco.classList.add('btn-turbo-fix');
            turbo.classList.remove('btn-turbo-fix');
            consoleLog.innerHTML += `<br>> Mode ÉCO activé : Économie d'énergie.`;
        }
        consoleLog.scrollTop = consoleLog.scrollHeight;
    }

    // --- 8. NEWS STREAM ---
    function updateNews() {
        const news = ["> ANALYSE : Nouveaux processeurs", "> CYBER : Alerte sécurité DNS", "> ROG : Firmware 1.4.2 déployé", "> SYSTEM : Intégrité 100%"];
        document.getElementById('news-stream').innerHTML = news.join('<br>');
    }

    // --- 9. EFFET SONORE CYBER ---
    let audioCtx = null;
    function playCyberSound() {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(1500, audioCtx.currentTime); 
        gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.05, audioCtx.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.05); 
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.05);
    }

// --- INITIALISATION DES ÉVÉNEMENTS ---
document.addEventListener('DOMContentLoaded', () => {
    // A. Interception des clics pour l'Explorateur (C:, E:, F:)
    document.body.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (link) {
            const href = link.getAttribute('href');
            // Si le lien commence par une lettre de lecteur Windows
            if (href && (href.startsWith('C:') || href.startsWith('E:') || href.startsWith('F:'))) {
                e.preventDefault(); // Empêche la navigation navigateur
                openFolder(href);
            }
        }
    });

    const cards = document.querySelectorAll('.card');
    cards.forEach(card => card.onmouseenter = () => playCyberSound());

    const buttons = document.querySelectorAll('.btn-short');
    buttons.forEach(btn => btn.onmouseenter = () => playCyberSound());

    const execBtn = document.querySelector('.search-form button');
    if (execBtn) execBtn.onmouseenter = () => playCyberSound();

    window.onclick = () => {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        audioCtx.resume();
    };

    setInterval(updateClock, 1000);
    setInterval(updateStats, 2000);
    setInterval(updateNetworkActivity, 1000);
    setInterval(getCrypto, 60000);
    setInterval(getRealWeather, 600000);

    updateClock(); updateStats(); getRealWeather(); getCrypto(); updateNews(); updateNetworkActivity();
});