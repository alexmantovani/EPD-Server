# Server e-Ink Display (EPD)

Server Flask per controllare un display e-Ink Waveshare 3.0" (400x168px, 4 colori) tramite chiamate HTTP POST.

## Caratteristiche

- **Display**: Waveshare 3.0" e-Paper (400x168px)
- **Colori supportati**: Bianco, Nero, Rosso, Giallo
- **6 template predefiniti** per diversi tipi di visualizzazione
- **API REST** per aggiornare il display in tempo reale
- **Stato iniziale** mostrato all'avvio del server

## Requisiti

- Python 3
- Raspberry Pi con display e-Ink Waveshare 3.0" collegato
- Librerie:
  - Flask
  - PIL (Pillow)
  - waveshare_epd

## Avvio del Server

```bash
python3 server_epd.py
```

Il server si avvia su `http://0.0.0.0:5000` e mostra immediatamente lo stato iniziale sul display con:
- IP della macchina
- Porta del server
- Stato "On Line..."

## API Endpoint

### POST `/update`

Aggiorna il contenuto del display utilizzando uno dei template disponibili.

**Content-Type**: `application/json`

**Body**: JSON con il campo `template` e i parametri specifici del template scelto.

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

## Esempi di Utilizzo

### Con curl

```bash
# Template WARNING
curl -X POST http://192.168.1.100:5000/update \
  -H "Content-Type: application/json" \
  -d '{
    "template": "warning",
    "top_text": "ERRORE",
    "line1": "Connessione persa",
    "line2": "Verificare la rete"
  }'

# Template STATUS
curl -X POST http://192.168.1.100:5000/update \
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
```

### Con Python (requests)

```python
import requests

url = "http://192.168.1.100:5000/update"

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

axios.post('http://192.168.1.100:5000/update', data)
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
eInk_Raspberry/
├── server_epd.py          # Server Flask principale
├── lib/                   # Librerie Waveshare
│   └── waveshare_epd/
├── pic/                   # Icone e font
│   ├── Font.ttc           # Font (obbligatorio)
│   ├── WARNING.bmp
│   ├── INFO.bmp
│   ├── CHECK.bmp
│   ├── ALERT.bmp
│   ├── STATUS.bmp
│   ├── WIFI.bmp
│   └── ...
└── README.md
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
- **Refresh**: Il display viene aggiornato immediatamente alla ricezione della richiesta POST
- **Delay**: 3 secondi di attesa dopo ogni aggiornamento del display

## Troubleshooting

### Icone non visualizzate

Assicurarsi che i file `.bmp` siano presenti nella directory `pic/` e abbiano i nomi corretti.

### Testo tagliato

Per il template `status`, se le label sono troppo lunghe, il testo potrebbe uscire dallo schermo. Usare label concise (max 12-15 caratteri).

### Colori sbagliati

Verificare che i nomi dei colori siano scritti in minuscolo: `"white"`, `"black"`, `"red"`, `"yellow"`.

## Licenza

Questo progetto utilizza le librerie Waveshare e-Paper. Consultare la documentazione Waveshare per i dettagli sulla licenza.
# EPD-Server
