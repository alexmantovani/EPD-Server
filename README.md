# Server e-Ink Display (EPD)

Server Flask per controllare un display e-Ink Waveshare 3.0" (400x168px, 4 colori) tramite chiamate HTTP POST.

## L'idea

Questo progetto trasforma un display e-Ink collegato a un Raspberry Pi in un **pannello informativo controllabile via HTTP**. L'idea è semplice: processi locali, script e applicazioni in esecuzione sul Raspberry Pi possono inviare richieste HTTP a localhost per aggiornare il contenuto del display in tempo reale.

### Casi d'uso

- **Dashboard di sistema**: Mostrare stato, IP, temperatura, RAM, CPU di server o Raspberry Pi
- **Notifiche visive**: Alert, warning, messaggi di errore da sistemi di monitoraggio
- **Status board**: Stato di servizi, backup, deployment, processi automatici
- **Home automation**: Integrare con Home Assistant, Node-RED, Domoticz
- **Sviluppo IoT**: Display per progetti embedded, sensori, stazioni meteo
- **Laboratorio/ufficio**: Pannello informativo per sale riunioni, laboratori, postazioni

### Come funziona

```
                    ┌──────────────────────────────────────────┐
                    │         Raspberry Pi (localhost)         │
                    │                                          │
┌─────────────┐     │   HTTP POST /update (127.0.0.1:5000)     │
│   Script    │────────>{"template": "status",                │
│   Python    │     │    "system_name": "SERVER",              │
│             │     │    "status": "ONLINE"}                   │
│             │     │                                          │
│             │<────────{"status": "OK", "queued": true}       │
└─────────────┘     │                                          │
                    │  ┌────────────┐                          │
                    │  │ Flask API  │                          │
                    │  │ (127.0.0.1)│                          │
                    │  └──────┬─────┘                          │
                    │         │                                │
                    │         ▼                                │
                    │  ┌────────────┐                          │
                    │  │   Queue    │                          │
                    │  │  (async)   │                          │
                    │  └──────┬─────┘                          │
                    │         │                                │
                    │         ▼                                │
                    │  ┌────────────┐                          │
                    │  │  Template  │                          │
                    │  │  Renderer  │                          │
                    │  └──────┬─────┘                          │
                    │         │                                │
                    │         ▼                                │
                    │  ┌────────────┐                          │
                    │  │  e-Ink     │                          │
                    │  │  Display   │                          │
                    │  └────────────┘                          │
                    └──────────────────────────────────────────┘
```

**Flusso di funzionamento:**

1. **Script locale invia richiesta HTTP POST** a localhost con i dati da visualizzare (template + parametri)
2. **Server Flask** (in ascolto su 127.0.0.1) valida la richiesta e la accoda immediatamente
3. **Risposta istantanea** allo script (non aspetta il refresh del display)
4. **Worker thread** processa la coda in modo asincrono
5. **Template renderer** genera l'immagine in base ai parametri ricevuti
6. **Display e-Ink** viene aggiornato con la nuova immagine

**Caratteristiche chiave:**

- **Aggiornamenti asincroni**: Le richieste HTTP ritornano immediatamente senza attendere il refresh del display (che può richiedere diversi secondi)
- **Coda intelligente**: Se arrivano multiple richieste, viene processata solo l'ultima (ottimizzazione)
- **Rate limiting**: Protezione hardware con limite di 1 aggiornamento ogni 10 secondi (preserva la durata del display e-Ink)
- **Template flessibili**: 6 template predefiniti per diversi tipi di visualizzazione
- **API REST semplice**: Facile integrazione con qualsiasi linguaggio o piattaforma

## Caratteristiche

- **Display**: Waveshare 3.0" e-Paper (400x168px)
- **Colori supportati**: Bianco, Nero, Rosso, Giallo
- **6 template predefiniti** per diversi tipi di visualizzazione
- **API REST** per aggiornare il display in tempo reale
- **Aggiornamenti asincroni** tramite coda thread-safe
- **Rate limiting** intelligente (max 1 aggiornamento ogni 10 secondi)
- **Supporto SVG completo** (file e inline) con colorazione dinamica
- **Upload immagini** tramite API (BMP, PNG, JPEG, GIF, SVG)
- **Monitoraggio stato** display in tempo reale
- **Test suite completa** con pytest
- **Stato iniziale** mostrato all'avvio del server

## Requisiti

- Python 3.7+
- Raspberry Pi con display e-Ink Waveshare 3.0" collegato
- Librerie Python:
  - Flask - Server web REST
  - Pillow (PIL) - Manipolazione immagini
  - waveshare_epd - Driver display e-paper
  - cairosvg - Supporto SVG (richiede cairo system library)

### Installazione dipendenze

```bash
# Dipendenze sistema (per cairosvg)
sudo apt-get install libcairo2-dev

# Dipendenze Python
pip install -r requirements.txt
```

## Collegamento Hardware (GPIO)

Il display e-Ink Waveshare 3.0" si collega al Raspberry Pi tramite interfaccia SPI e GPIO.

### Schema dei collegamenti

| Pin Display | Funzione | GPIO (BCM) | Pin Fisico |
|-------------|----------|------------|------------|
| VCC         | Alimentazione 3.3V | - | Pin 1 o 17 (3.3V) |
| GND         | Ground | - | Pin 6, 9, 14, 20, 25, 30, 34, 39 |
| DIN (MOSI)  | SPI Data In | GPIO 10 | Pin 19 |
| CLK (SCLK)  | SPI Clock | GPIO 11 | Pin 23 |
| CS          | Chip Select | GPIO 8 (CE0) | Pin 24 |
| DC          | Data/Command | GPIO 25 | Pin 22 |
| RST         | Reset | GPIO 17 | Pin 11 |
| BUSY        | Busy Signal | GPIO 24 | Pin 18 |
| PWR         | Power Control | GPIO 18 | Pin 12 |

### Dettagli tecnici

- **Interfaccia**: SPI (bus 0, device 0)
- **Velocità SPI**: 4 MHz
- **Modalità SPI**: Mode 0 (CPOL=0, CPHA=0)
- **Alimentazione**: 3.3V (NON usare 5V!)
- **Numerazione GPIO**: BCM (Broadcom)

### Note importanti

- Assicurarsi che l'interfaccia SPI sia abilitata sul Raspberry Pi:
  ```bash
  sudo raspi-config
  # Interfacing Options -> SPI -> Enable
  ```
- Utilizzare **solo alimentazione 3.3V**, non 5V
- I pin GPIO sono configurati automaticamente dal driver `epdconfig.py`
- Il pin PWR (GPIO 18) controlla l'alimentazione del display

## Quick Start

```bash
# 1. Installa dipendenze
sudo apt-get install libcairo2-dev
pip install -r requirements.txt

# 2. Avvia il server
python3 server.py

# 3. Testa l'API
curl http://localhost:5000/status

# 4. Aggiorna il display
curl -X POST http://localhost:5000/update \
  -H "Content-Type: application/json" \
  -d '{"template": "status", "system_name": "TEST", "status": "ONLINE"}'
```

## Avvio del Server

```bash
python3 server.py
```

Il server si avvia su `http://127.0.0.1:5000` e:
- Avvia un worker thread per gli aggiornamenti asincroni
- Mostra lo stato iniziale sul display con IP, porta e status
- Accetta richieste HTTP solo da localhost su tutti i 3 endpoint disponibili

## API Endpoint

### POST `/update`

Aggiorna il contenuto del display utilizzando uno dei template disponibili.

**Content-Type**: `application/json`

**Body**: JSON con il campo `template` e i parametri specifici del template scelto.

**Risposta successo:**
```json
{
  "status": "OK",
  "template": "status",
  "queued": true
}
```

**Note:**
- Le richieste vengono accodate e processate in modo asincrono
- Il server risponde immediatamente senza attendere l'aggiornamento del display
- Se la coda è piena, ritorna HTTP 503 (Service Unavailable)
- Gli aggiornamenti sono limitati a 1 ogni 10 secondi (protezione hardware)
- Se ci sono multiple richieste in coda, viene processata solo l'ultima

---

### GET `/status`

Restituisce lo stato corrente del display.

**Risposta:**
```json
{
  "template": "status",
  "data": {
    "system_name": "EPD SERVER",
    "status": "ONLINE",
    ...
  },
  "status": "ready",
  "queue_size": 0,
  "last_update": "2025-11-29T12:34:56.789",
  "seconds_since_update": 5.2
}
```

**Campi:**
- `template`: Nome del template correntemente visualizzato
- `data`: Dati utilizzati per generare l'immagine corrente
- `status`: Stato del display (`initializing`, `ready`, `error`)
- `queue_size`: Numero di aggiornamenti in coda
- `last_update`: Timestamp ISO dell'ultimo aggiornamento (se disponibile)
- `seconds_since_update`: Secondi trascorsi dall'ultimo aggiornamento (se disponibile)

---

### POST `/upload`

Carica un'immagine nella cartella `pic/` per usarla come icona nei template.

**Content-Type**: `multipart/form-data`

**Parametri:**
- `file`: File immagine (obbligatorio)
- `name`: Nome personalizzato per il file (opzionale, mantiene l'estensione originale)

**Formati supportati:**
- PNG (.png)
- JPEG (.jpg, .jpeg)
- BMP (.bmp)
- GIF (.gif)
- SVG (.svg)

**Dimensione massima:** 10 MB

**Esempio con curl:**
```bash
# Upload base
curl -X POST -F "file=@icon.svg" http://localhost:5000/upload

# Upload con nome personalizzato
curl -X POST \
  -F "file=@myicon.png" \
  -F "name=CUSTOM_ICON" \
  http://localhost:5000/upload
```

**Risposta successo:**
```json
{
  "status": "OK",
  "filename": "icon.svg",
  "path": "pic/icon.svg",
  "size_bytes": 2048
}
```

**Risposta errore (estensione non valida):**
```json
{
  "error": "Tipo file non consentito",
  "allowed_extensions": ["png", "jpg", "jpeg", "bmp", "gif", "svg"]
}
```

## Template Disponibili

### 1. WARNING

Template per messaggi di avviso con area rossa e icona.

**Parametri:**
- `template`: `"warning"` (obbligatorio)
- `top_text`: Testo nella banda nera superiore (default: `"WARNING"`)
- `icon`: Nome file icona in `pic/` (default: `"WARNING.bmp"`)
- `line1`: Prima riga di testo (colore bianco)
- `line2`: Seconda riga di testo (colore bianco)

**Esempio:**
```json
{
  "template": "warning",
  "top_text": "ATTENZIONE",
  "icon": "WARNING.bmp",
  "line1": "Temperatura elevata",
  "line2": "Controllare il sistema"
}
```

**Layout:**
```
┌─────────────────────────────────┐
│  [BANDA NERA]                   │
│  ATTENZIONE (centrato, bianco)  │
├─────────────────────────────────┤
│  [AREA ROSSA]                   │
│  [ICONA]  Temperatura elevata   │
│           Controllare il sistema│
└─────────────────────────────────┘
```

---

### 2. INFO

Template informativo con banda nera e 2-3 righe di testo centrate verticalmente.

**Parametri:**
- `template`: `"info"` (obbligatorio)
- `title`: Titolo nella banda nera superiore (default: `"INFORMATION"`)
- `icon`: Nome file icona in `pic/` (default: `"INFO.bmp"`)
- `line1`: Prima riga di testo
- `line2`: Seconda riga di testo
- `line3`: Terza riga di testo (opzionale)

**Esempio:**
```json
{
  "template": "info",
  "title": "SISTEMA",
  "icon": "INFO.bmp",
  "line1": "Temperatura: 45°C",
  "line2": "CPU: 20%",
  "line3": "RAM: 512MB"
}
```

**Layout:**
```
┌─────────────────────────────────┐
│  [BANDA NERA]                   │
│  SISTEMA (centrato, bianco)     │
├─────────────────────────────────┤
│  [SFONDO BIANCO]                │
│  [ICONA]  Temperatura: 45°C     │
│           CPU: 20%              │
│           RAM: 512MB            │
│  (testo centrato verticalmente) │
└─────────────────────────────────┘
```

---

### 3. SUCCESS

Template per conferme di operazioni riuscite con banner nero.

**Parametri:**
- `template`: `"success"` (obbligatorio)
- `title`: Titolo (default: `"SUCCESS"`)
- `message`: Messaggio in basso (default: `"Operation completed"`)
- `icon`: Nome file icona in `pic/` (default: `"CHECK.bmp"`)

**Esempio:**
```json
{
  "template": "success",
  "title": "COMPLETATO",
  "message": "Aggiornamento installato",
  "icon": "CHECK.bmp"
}
```

**Layout:**
```
┌─────────────────────────────────┐
│  [BANNER NERO]                  │
│  COMPLETATO (centrato, bianco)  │
├─────────────────────────────────┤
│  [SFONDO BIANCO]                │
│                                 │
│        [ICONA CENTRATA]         │
│                                 │
│  Aggiornamento installato       │
│         (centrato, basso)       │
└─────────────────────────────────┘
```

---

### 4. ALERT

Template per avvisi urgenti con sfondo giallo e header rosso.

**Parametri:**
- `template`: `"alert"` (obbligatorio)
- `title`: Titolo nell'header rosso (default: `"ALERT"`)
- `subtitle`: Sottotitolo (opzionale)
- `line1`: Prima riga di dettagli
- `line2`: Seconda riga di dettagli
- `line3`: Terza riga di dettagli
- `icon`: Nome file icona in `pic/` (default: `"ALERT.bmp"`)

**Esempio:**
```json
{
  "template": "alert",
  "title": "EMERGENZA",
  "subtitle": "Sistema critico",
  "line1": "Temperatura: 85°C",
  "line2": "Disk: 98% full",
  "line3": "Azione richiesta",
  "icon": "ALERT.bmp"
}
```

**Layout:**
```
┌─────────────────────────────────┐
│  [HEADER ROSSO]                 │
│  EMERGENZA (centrato, bianco)   │
├─────────────────────────────────┤
│  [SFONDO GIALLO]                │
│  [ICONA]  Sistema critico       │
│           Temperatura: 85°C     │
│           Disk: 98% full        │
│           Azione richiesta      │
│  (testo centrato verticalmente) │
└─────────────────────────────────┘
```

---

### 5. STATUS

Template per mostrare lo stato di un sistema con campi organizzati.

**Parametri:**
- `template`: `"status"` (obbligatorio)
- `system_name`: Nome del sistema (es. `"EPD SERVER"`)
- `status`: Stato del sistema (`"ONLINE"` o altro)
  - `"ONLINE"` → badge nero
  - Altro → badge rosso
- `field1_label`: Etichetta primo campo
- `field1_value`: Valore primo campo
- `field2_label`: Etichetta secondo campo
- `field2_value`: Valore secondo campo
- `field3_label`: Etichetta terzo campo
- `field3_value`: Valore terzo campo
- `icon`: Nome file icona in `pic/` (default: `"STATUS.bmp"`)

**Esempio:**
```json
{
  "template": "status",
  "system_name": "WEB SERVER",
  "status": "ONLINE",
  "field1_label": "IP",
  "field1_value": "192.168.1.100",
  "field2_label": "Porta",
  "field2_value": "8080",
  "field3_label": "Uptime",
  "field3_value": "24h",
  "icon": "STATUS.bmp"
}
```

**Layout:**
```
┌─────────────────────────────────┐
│  [HEADER NERO]                  │
│  WEB SERVER    [ONLINE]         │
│  (sinistra)    (badge, destra)  │
├─────────────────────────────────┤
│  [SFONDO BIANCO]                │
│  [ICONA]  IP:      192.168.1.100│
│           Porta:   8080         │
│           Uptime:  24h          │
│  (valori allineati)             │
└─────────────────────────────────┘
```

**Note:**
- Le etichette sono allineate a sinistra
- I valori sono allineati verticalmente in base alla label più lunga
- Il badge status cambia colore: nero per `"ONLINE"`, rosso per altri stati

---

### 6. SIMPLE

Template minimalista con testo centrato e sfondo personalizzabile.

**Parametri:**
- `template`: `"simple"` (obbligatorio)
- `title`: Titolo (font grande)
- `message`: Messaggio centrale (font piccolo)
- `footer`: Testo in basso (font piccolo)
- `bg_color`: Colore di sfondo (default: `"white"`)
  - Valori: `"white"`, `"black"`, `"red"`, `"yellow"`
- `color`: Colore del testo (opzionale)
  - Valori: `"white"`, `"black"`, `"red"`, `"yellow"`
  - Se non specificato, viene scelto automaticamente in base allo sfondo

**Esempio 1 (colore automatico):**
```json
{
  "template": "simple",
  "title": "MANUTENZIONE",
  "message": "Sistema in pausa",
  "footer": "Ritorno previsto: 14:00",
  "bg_color": "red"
}
```

**Esempio 2 (colore personalizzato):**
```json
{
  "template": "simple",
  "title": "BENVENUTO",
  "message": "Sistema pronto",
  "bg_color": "white",
  "color": "red"
}
```

**Layout:**
```
┌─────────────────────────────────┐
│                                 │
│         MANUTENZIONE            │
│       (centrato, 1/3 alto)      │
│                                 │
│      Sistema in pausa           │
│       (centrato, metà)          │
│                                 │
│    Ritorno previsto: 14:00      │
│       (centrato, basso)         │
└─────────────────────────────────┘
```

---

## Colori Supportati

Il display e-Ink 3.0" supporta **4 colori**:

- `epd.WHITE` - Bianco
- `epd.BLACK` - Nero
- `epd.RED` - Rosso
- `epd.YELLOW` - Giallo

**Nota**: Il verde NON è supportato da questo display.

---

## Supporto SVG

Tutti i template supportano icone in formato SVG, sia come file che come dati inline. Le icone SVG vengono automaticamente:
- Convertite in immagini 72x72px
- Colorate dinamicamente in base al template (nero, bianco, rosso)
- Rese con trasparenza (alpha channel)

### Uso con file SVG

```bash
# 1. Carica l'icona SVG sul server
curl -X POST -F "file=@home.svg" http://localhost:5000/upload

# 2. Usala in un template
curl -X POST http://localhost:5000/update \
  -H "Content-Type: application/json" \
  -d '{
    "template": "status",
    "system_name": "HOME SERVER",
    "status": "ONLINE",
    "icon": "home.svg"
  }'
```

### Uso con SVG inline

Puoi passare l'SVG direttamente nel parametro `svg`:

```bash
curl -X POST http://localhost:5000/update \
  -H "Content-Type: application/json" \
  -d '{
    "template": "status",
    "system_name": "EPD SERVER",
    "status": "ONLINE",
    "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"72\" height=\"72\" viewBox=\"0 0 24 24\"><path d=\"M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z\" fill=\"currentColor\"/></svg>"
  }'
```

### Colorazione automatica

Le icone SVG vengono colorate automaticamente in base al template:
- **status**: Nero o rosso (in base allo stato)
- **warning**: Bianco
- **alert**: Nero
- **success**: Nero
- **info**: Nero

Il sistema sostituisce automaticamente:
- `currentColor`
- `fill="black"` o `fill="#000"`
- `stroke="black"` o `stroke="#000"`

---

## Esempi di Utilizzo

### Con curl

```bash
# Controlla stato corrente
curl http://localhost:5000/status

# Template WARNING
curl -X POST http://localhost:5000/update \
  -H "Content-Type: application/json" \
  -d '{
    "template": "warning",
    "top_text": "ERRORE",
    "line1": "Connessione persa",
    "line2": "Verificare la rete"
  }'

# Template STATUS
curl -X POST http://localhost:5000/update \
  -H "Content-Type: application/json" \
  -d '{
    "template": "status",
    "system_name": "RASPBERRY PI",
    "status": "ONLINE",
    "field1_label": "Temperatura",
    "field1_value": "45°C",
    "field2_label": "CPU",
    "field2_value": "15%",
    "field3_label": "RAM",
    "field3_value": "512MB"
  }'

# Upload icona SVG
curl -X POST -F "file=@icon.svg" http://localhost:5000/upload
```

### Con Python (requests)

```python
import requests

url = "http://localhost:5000/update"

# Esempio INFO
data = {
    "template": "info",
    "title": "NOTIFICA",
    "line1": "Backup completato",
    "line2": "File: 1250",
    "line3": "Size: 2.4GB"
}

response = requests.post(url, json=data)
print(response.json())
```

### Con Node.js (axios)

```javascript
const axios = require('axios');

const data = {
  template: 'alert',
  title: 'ATTENZIONE',
  subtitle: 'Spazio disco',
  line1: 'Disco quasi pieno',
  line2: 'Liberare spazio',
  icon: 'ALERT.bmp'
};

axios.post('http://localhost:5000/update', data)
  .then(response => console.log(response.data))
  .catch(error => console.error(error));
```

## Risposte del Server

### Successo

```json
{
  "status": "OK",
  "template": "warning"
}
```

### Errore (template non trovato)

```json
{
  "error": "Template 'invalid' non trovato. Disponibili: ['warning', 'info', 'success', 'alert', 'status', 'simple']"
}
```

Status code: `400`

### Errore generico

```json
{
  "error": "Messaggio di errore"
}
```

Status code: `500`

## Struttura Directory

```
EPD-Server/
├── server.py              # Server Flask principale
├── epd_manager.py         # Manager per il display e-paper
├── utils.py               # Utility functions (SVG, IP, bbox, load_icon)
├── config.py              # Configurazione (font, colori, path)
├── lib/                   # Librerie Waveshare
│   └── waveshare_epd/
├── pic/                   # Icone e font
│   ├── Font.ttc           # Font (obbligatorio)
│   ├── WARNING.bmp
│   ├── INFO.bmp
│   ├── ALERT.bmp
│   ├── WIFI.bmp
│   └── ...                # Icone caricate via /upload
├── templates/             # Template di rendering
│   ├── __init__.py
│   ├── status.py
│   ├── warning.py
│   ├── alert.py
│   ├── success.py
│   ├── info.py
│   └── simple.py
├── tests/                 # Test suite
│   ├── conftest.py        # Configurazione pytest
│   ├── test_server.py     # Test endpoint HTTP
│   ├── test_utils.py      # Test utility functions
│   └── test_templates.py  # Test template rendering
├── requirements.txt       # Dipendenze produzione
├── requirements-dev.txt   # Dipendenze sviluppo/test
├── README.md              # Documentazione principale
└── README_TESTS.md        # Documentazione test
```

## Avvio automatico (systemd)

Il modo migliore per avviare automaticamente un programma Python su
Raspberry Pi è creare un servizio `systemd`. Questo assicura che il
server parta al boot, venga riavviato se crasha e possa essere gestito
come un normale servizio Linux.

### Crea il file di servizio

Apri il file:

```bash
sudo nano /etc/systemd/system/epdserver.service
```

Inserisci dentro:

```ini
[Unit]
Description=EPD Display Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/EPD-Server/server.py
WorkingDirectory=/home/pi/EPD-Server
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

### Ricarica systemd

```bash
sudo systemctl daemon-reload
```

### Abilita l'avvio automatico

```bash
sudo systemctl enable epdserver
```

### Avvia il servizio subito

```bash
sudo systemctl start epdserver
```

### Controlla lo stato

```bash
systemctl status epdserver
```

### Controlla i log

```bash
journalctl -u epdserver -f
```

Così il server Python partirà sempre all'accensione e verrà riavviato in
caso di errori.

## Note Tecniche

- **Display**: 400x168px in modalità landscape
- **Font**:
  - Grande: 40pt (`font_big`)
  - Piccolo: 24pt (`font_small`)
- **Refresh**: Gli aggiornamenti vengono accodati e processati asincronamente
- **Rate Limiting**: Massimo 1 aggiornamento ogni 10 secondi (protezione hardware e-paper)
- **Coda**: Massimo 10 richieste in coda; se piena, le richieste vengono rifiutate con HTTP 503
- **Threading**: Worker thread dedicato per gli aggiornamenti del display
- **Ottimizzazione**: Se ci sono multiple richieste in coda, viene processata solo l'ultima (più recente)

## Troubleshooting

### Icone non visualizzate

Assicurarsi che i file `.bmp` siano presenti nella directory `pic/` e abbiano i nomi corretti.

### Testo tagliato

Per il template `status`, se le label sono troppo lunghe, il testo potrebbe uscire dallo schermo. Usare label concise (max 12-15 caratteri).

### Colori sbagliati

Verificare che i nomi dei colori siano scritti in minuscolo: `"white"`, `"black"`, `"red"`, `"yellow"`.

---

## Test

Il progetto include una suite di test completa con pytest.

### Installazione dipendenze di test

```bash
pip install -r requirements-dev.txt
```

### Esecuzione test

```bash
# Tutti i test
pytest

# Test con output verboso
pytest -v

# Test con coverage
pytest --cov=. --cov-report=html

# Test specifici
pytest tests/test_server.py
pytest tests/test_utils.py
pytest tests/test_templates.py
```

### Struttura test

- **tests/test_server.py**: Test degli endpoint HTTP (`/update`, `/status`, `/upload`)
- **tests/test_utils.py**: Test delle utility (`bbox`, `get_ip`, `svg_to_image`, `load_icon`)
- **tests/test_templates.py**: Test dei template di rendering (status, warning, alert, success, info)
- **tests/conftest.py**: Fixture comuni e configurazione pytest

### Coverage

Il progetto ha una copertura di test >95%. Per vedere il report dettagliato:

```bash
pytest --cov=. --cov-report=term-missing
```

Per maggiori dettagli, consulta [README_TESTS.md](README_TESTS.md).

---

## Licenza

Questo progetto utilizza le librerie Waveshare e-Paper. Consultare la documentazione Waveshare per i dettagli sulla licenza.
# EPD-Server
