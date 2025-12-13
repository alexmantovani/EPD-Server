# Sistema di Logging EPD-Server

Questo documento descrive il sistema di logging implementato nel progetto EPD-Server.

## Panoramica

Il sistema di logging è centralizzato nel modulo `logger.py` e offre:

- **Logging su file e console** con formati diversi
- **Rotazione automatica** dei file di log (massimo 10MB per file)
- **Log separati per errori** (`epd-server-errors.log`)
- **Colori nella console** per una migliore leggibilità
- **Livelli di log configurabili** (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Struttura dei File di Log

I log vengono salvati nella cartella `logs/` (creata automaticamente):

```
logs/
├── epd-server.log          # Log completo di tutte le operazioni
└── epd-server-errors.log   # Solo errori (ERROR e CRITICAL)
```

### Rotazione dei Log

- Dimensione massima per file: **10 MB**
- Backup mantenuti: **5 file**
- Quando un file raggiunge 10MB, viene rinominato (es. `epd-server.log.1`) e ne viene creato uno nuovo

## Livelli di Log

| Livello | Descrizione | Uso |
|---------|-------------|-----|
| **DEBUG** | Informazioni dettagliate per debugging | Dimensioni immagini, parametri template, dettagli operazioni |
| **INFO** | Conferme operazioni normali | Avvio server, display aggiornato, file salvato |
| **WARNING** | Avvisi (situazioni anomale ma gestibili) | Coda piena, file non trovato, template non valido |
| **ERROR** | Errori che impediscono un'operazione | Fallimento rendering, errore I/O, eccezioni |
| **CRITICAL** | Errori gravi che potrebbero bloccare il sistema | Non utilizzato al momento |

## Formato dei Log

### Console (colorato)
```
14:23:45 | INFO     | EPD Server logging system initialized
14:23:45 | INFO     | Starting EPD Server
14:23:46 | DEBUG    | Ricevuta richiesta POST /update da 127.0.0.1
14:23:46 | ERROR    | Errore nel rendering HTML: Invalid HTML syntax
```

### File (dettagliato)
```
2024-12-12 14:23:45 | INFO     | epd-server | logger:init_logging:143 | EPD Server logging system initialized
2024-12-12 14:23:45 | INFO     | epd-server.server | server:<module>:242 | Starting EPD Server
2024-12-12 14:23:46 | DEBUG    | epd-server.server | server:update_display:101 | Ricevuta richiesta POST /update da 127.0.0.1
2024-12-12 14:23:46 | ERROR    | epd-server.templates.html | html:template_html:96 | Errore nel rendering HTML: Invalid HTML syntax
```

## Configurazione

### Modalità Debug

Per abilitare il livello DEBUG, imposta la variabile d'ambiente `DEBUG_MODE`:

```bash
# Linux/Mac
export DEBUG_MODE=true
python server.py

# Windows
set DEBUG_MODE=true
python server.py
```

In modalità DEBUG vedrai log molto dettagliati:
- Parametri ricevuti da ogni endpoint
- Dimensioni delle immagini generate
- Tempo di esecuzione delle operazioni
- Dettagli interni dei template

### Modalità Normale (INFO)

Avvia il server normalmente per log essenziali:

```bash
python server.py
```

## Uso nei Moduli

### Creare un Logger

```python
from logger import get_logger

# Logger per il modulo corrente
logger = get_logger('nome_modulo')

# Esempi
logger = get_logger('templates.custom')
logger = get_logger('utils')
```

### Esempi di Log

```python
# Informazioni generali
logger.info("Operazione completata con successo")

# Debug dettagliato
logger.debug(f"Parametri ricevuti: {data}")

# Warning
logger.warning("File non trovato, uso default")

# Errore con traceback completo
try:
    risky_operation()
except Exception as e:
    logger.error(f"Errore: {e}", exc_info=True)  # exc_info=True include il traceback
```

## Logger Attivi nel Progetto

| Modulo | Logger | Descrizione |
|--------|--------|-------------|
| `server.py` | `epd-server.server` | HTTP endpoints, worker thread, gestione coda |
| `epd_manager.py` | `epd-server.epd_manager` | Inizializzazione display, visualizzazione immagini |
| `templates/html.py` | `epd-server.templates.html` | Rendering HTML to image |
| `templates/message.py` | `epd-server.templates.message` | Generazione template message |

## Esempi di Output

### Avvio Server (INFO)
```
============================================================
EPD Server logging system initialized
Log level: INFO
============================================================
Inizializzazione EPD Manager...
EPD Manager inizializzato con successo (dimensioni: 400x168)
============================================================
Starting EPD Server
============================================================
Avvio worker thread per aggiornamento display...
Display worker thread avviato
Worker thread avviato con successo
Generazione schermata di status iniziale...
Schermata di status aggiunta alla coda
Avvio server Flask su http://127.0.0.1:5000
Templates disponibili: ['warning', 'info', 'success', 'alert', 'status', 'simple', 'html', 'message']
============================================================
```

### Richiesta Template (DEBUG)
```
14:30:12 | DEBUG    | Ricevuta richiesta POST /update da 127.0.0.1
14:30:12 | DEBUG    | Template richiesto: 'message'
14:30:12 | DEBUG    | Generazione immagine con template 'message'
14:30:12 | DEBUG    | template_message chiamato con dimensioni 400x168
14:30:12 | DEBUG    | Parametri: bg=red, color=white, title='Errore', message='Scheda non valida', icon=alert.bmp
14:30:12 | DEBUG    | Caricamento icona: alert.bmp
14:30:12 | DEBUG    | Icona caricata: (72, 72)
14:30:12 | INFO     | Template message generato con successo (400x168, bg=red, icon=sì)
14:30:12 | DEBUG    | Immagine generata con successo: (400, 168)
14:30:12 | INFO     | Immagine 'message' aggiunta alla coda (dimensione: 1)
```

### Errore HTML Rendering (ERROR)
```
14:35:22 | ERROR    | Errore nel rendering HTML: HTML parsing error
Traceback (most recent call last):
  File "/path/to/templates/html.py", line 70, in template_html
    html_doc = HTML(string=html_with_viewport)
  File "/path/to/weasyprint/__init__.py", line 142, in __init__
    raise ValueError("Invalid HTML")
ValueError: Invalid HTML
14:35:22 | WARNING  | Creazione immagine di errore fallback...
14:35:22 | INFO     | Immagine di errore fallback creata
```

## Troubleshooting

### I log non vengono salvati su file

1. Verifica che la cartella `logs/` esista e sia scrivibile
2. Controlla i permessi: `chmod 755 logs/`
3. Verifica spazio su disco

### Troppi log (file troppo grandi)

Riduci il livello di log da DEBUG a INFO:
```python
# In logger.py, modifica init_logging
init_logging(level=logging.INFO, debug_mode=False)
```

### Non vedo i log colorati

I colori potrebbero non funzionare su alcuni terminali Windows. Disabilita i colori:
```python
# In logger.py
setup_logger(..., colored_console=False)
```

## Best Practices

1. **Usa DEBUG per dettagli tecnici**
   ```python
   logger.debug(f"Dimensioni: {width}x{height}, Mode: {mode}")
   ```

2. **Usa INFO per conferme operative**
   ```python
   logger.info("Display aggiornato con successo")
   ```

3. **Usa WARNING per anomalie gestibili**
   ```python
   logger.warning("Coda display piena, richiesta rifiutata")
   ```

4. **Usa ERROR con exc_info=True per eccezioni**
   ```python
   except Exception as e:
       logger.error(f"Errore: {e}", exc_info=True)
   ```

5. **Non loggare dati sensibili**
   ```python
   # ❌ NO
   logger.info(f"Password: {password}")

   # ✅ SI
   logger.info("Autenticazione completata")
   ```

6. **Usa stringhe f-string per lazy evaluation**
   ```python
   # Meglio performance (la stringa viene costruita solo se il log viene scritto)
   logger.debug(f"Dati: {expensive_operation()}")
   ```

## Manutenzione

### Pulizia Log Vecchi

I file di log vengono ruotati automaticamente, ma puoi pulire manualmente:

```bash
# Rimuovi tutti i log
rm -rf logs/

# Rimuovi solo i backup
rm logs/*.log.*

# Mantieni solo i log recenti (ultimi 7 giorni)
find logs/ -name "*.log*" -mtime +7 -delete
```

### Analisi Log

```bash
# Cerca errori
grep ERROR logs/epd-server.log

# Solo errori critici
grep -E "ERROR|CRITICAL" logs/epd-server.log

# Conta richieste per template
grep "Template richiesto" logs/epd-server.log | cut -d"'" -f2 | sort | uniq -c

# Ultimi 50 log
tail -n 50 logs/epd-server.log

# Segui log in tempo reale
tail -f logs/epd-server.log
```

## Performance

Il sistema di logging ha un overhead minimo:
- **DEBUG mode**: ~5-10% overhead (solo per development)
- **INFO mode**: ~1-2% overhead (accettabile per production)

Per prestazioni massime in production, considera di ridurre a WARNING:
```python
init_logging(level=logging.WARNING)
```
