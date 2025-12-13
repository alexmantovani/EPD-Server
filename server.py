from flask import Flask, request, jsonify
import time
import threading
import queue
import os
from werkzeug.utils import secure_filename

from epd_manager import EPDManager
from templates import TEMPLATES
from config import PICDIR
from logger import init_logging, get_logger

app = Flask(__name__)

# Inizializza il sistema di logging
# Usa DEBUG_MODE=True nella variabile d'ambiente per debug level
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
init_logging(debug_mode=DEBUG_MODE)

# Logger per il server
logger = get_logger('server')

# Configurazione upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'svg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

epd = EPDManager()

# Coda thread-safe per le immagini da visualizzare
display_queue = queue.Queue(maxsize=10)

# Intervallo minimo tra aggiornamenti del display (in secondi)
MIN_UPDATE_INTERVAL = 10
last_update_time = 0

# Stato corrente del display
current_display_state = {
    "template": None,
    "data": None,
    "timestamp": None,
    "status": "initializing"
}

def display_worker():
    """Worker thread che consuma la coda e aggiorna il display"""
    global last_update_time, current_display_state

    logger.info("Display worker thread avviato")
    while True:
        try:
            # Attende un'immagine dalla coda (bloccante)
            logger.debug("Attendo immagine dalla coda...")
            img, template_name, data = display_queue.get()
            logger.debug(f"Ricevuta richiesta per template '{template_name}'")

            # Se ci sono altre immagini in coda, prendi solo l'ultima (scarta quelle intermedie)
            skipped = 0
            while not display_queue.empty():
                try:
                    display_queue.task_done()  # Marca come completata quella che stiamo scartando
                    img, template_name, data = display_queue.get_nowait()
                    skipped += 1
                except queue.Empty:
                    break

            if skipped > 0:
                logger.info(f"Saltate {skipped} richieste intermedie, processo solo l'ultima: {template_name}")

            # Calcola il tempo trascorso dall'ultimo aggiornamento
            elapsed = time.time() - last_update_time

            # Se non sono passati almeno MIN_UPDATE_INTERVAL secondi, aspetta
            if elapsed < MIN_UPDATE_INTERVAL:
                wait_time = MIN_UPDATE_INTERVAL - elapsed
                logger.info(f"Attendo {wait_time:.1f}s prima del prossimo aggiornamento (ultimo: {elapsed:.1f}s fa)")
                time.sleep(wait_time)

            logger.info(f"Aggiornamento display con template: {template_name}")
            logger.debug(f"Dimensioni immagine: {img.size}, Mode: {img.mode}")

            epd.show(img)
            last_update_time = time.time()

            # Aggiorna lo stato corrente del display
            current_display_state.update({
                "template": template_name,
                "data": data,
                "timestamp": last_update_time,
                "status": "ready"
            })

            display_queue.task_done()
            logger.info("Display aggiornato con successo")
        except Exception as e:
            logger.error(f"Errore nell'aggiornamento del display: {e}", exc_info=True)
            current_display_state["status"] = "error"
            display_queue.task_done()

@app.route("/update", methods=["POST"])
def update_display():
    logger.debug(f"Ricevuta richiesta POST /update da {request.remote_addr}")

    data = request.json
    if not data:
        logger.warning("Richiesta /update senza JSON body")
        return jsonify({"error": "JSON body richiesto"}), 400

    name = data.get("template", "warning")
    logger.debug(f"Template richiesto: '{name}'")

    if name not in TEMPLATES:
        logger.warning(f"Template non valido richiesto: '{name}'")
        return jsonify({
            "error": "Template non valido",
            "available_templates": list(TEMPLATES.keys())
        }), 400

    template = TEMPLATES[name]
    logger.debug(f"Generazione immagine con template '{name}'")

    try:
        # genera immagine
        img = template(
            data,
            epd.WIDTH,
            epd.HEIGHT,
            epd_colors={"WHITE": epd.epd.WHITE, "BLACK": epd.epd.BLACK,
                        "RED": epd.epd.RED, "YELLOW": epd.epd.YELLOW}
        )
        logger.debug(f"Immagine generata con successo: {img.size}")
    except Exception as e:
        logger.error(f"Errore nella generazione dell'immagine con template '{name}': {e}", exc_info=True)
        return jsonify({"error": f"Errore nella generazione dell'immagine: {str(e)}"}), 500

    # Aggiungi l'immagine alla coda invece di bloccare
    try:
        display_queue.put((img, name, data), timeout=2)
        logger.info(f"Immagine '{name}' aggiunta alla coda (dimensione: {display_queue.qsize()})")
        return jsonify({"status": "OK", "template": name, "queued": True})
    except queue.Full:
        logger.warning("Coda display piena, richiesta rifiutata")
        return jsonify({"error": "Display occupato, riprova tra poco"}), 503

@app.route("/status", methods=["GET"])
def get_display_status():
    """Restituisce lo stato corrente del display"""
    logger.debug(f"Ricevuta richiesta GET /status da {request.remote_addr}")

    response = {
        "template": current_display_state["template"],
        "data": current_display_state["data"],
        "status": current_display_state["status"],
        "queue_size": display_queue.qsize()
    }

    # Aggiungi timestamp formattato se disponibile
    if current_display_state["timestamp"]:
        from datetime import datetime
        response["last_update"] = datetime.fromtimestamp(current_display_state["timestamp"]).isoformat()
        response["seconds_since_update"] = time.time() - current_display_state["timestamp"]

    logger.debug(f"Status response: {response}")
    return jsonify(response)

def allowed_file(filename):
    """Verifica se l'estensione del file è consentita"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_image():
    """Carica un'immagine nella cartella pic/"""
    logger.debug(f"Ricevuta richiesta POST /upload da {request.remote_addr}")

    # Verifica che ci sia un file nella richiesta
    if 'file' not in request.files:
        logger.warning("Richiesta /upload senza file")
        return jsonify({"error": "Nessun file fornito"}), 400

    file = request.files['file']

    # Verifica che sia stato selezionato un file
    if file.filename == '':
        logger.warning("Richiesta /upload con filename vuoto")
        return jsonify({"error": "Nessun file selezionato"}), 400

    logger.debug(f"File ricevuto: {file.filename}")

    # Verifica l'estensione del file
    if not allowed_file(file.filename):
        logger.warning(f"Tentativo di upload file non consentito: {file.filename}")
        return jsonify({
            "error": "Tipo file non consentito",
            "allowed_extensions": list(ALLOWED_EXTENSIONS)
        }), 400

    # Verifica la dimensione del file
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    logger.debug(f"Dimensione file: {file_size} bytes ({file_size / (1024 * 1024):.2f} MB)")

    if file_size > MAX_FILE_SIZE:
        logger.warning(f"File troppo grande: {file_size} bytes (max: {MAX_FILE_SIZE})")
        return jsonify({
            "error": "File troppo grande",
            "max_size_mb": MAX_FILE_SIZE / (1024 * 1024),
            "file_size_mb": file_size / (1024 * 1024)
        }), 400

    # Sanitizza il nome del file
    filename = secure_filename(file.filename)

    # Ottieni il nome personalizzato se fornito
    custom_name = request.form.get('name')
    if custom_name:
        # Mantieni l'estensione originale
        ext = filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(custom_name) + '.' + ext
        logger.debug(f"Nome personalizzato richiesto: {filename}")

    # Salva il file
    filepath = os.path.join(PICDIR, filename)

    try:
        file.save(filepath)
        logger.info(f"File salvato: {filepath} ({file_size} bytes)")

        return jsonify({
            "status": "OK",
            "filename": filename,
            "path": filepath,
            "size_bytes": file_size
        }), 201

    except Exception as e:
        logger.error(f"Errore durante il salvataggio del file: {e}", exc_info=True)
        return jsonify({"error": "Errore durante il salvataggio del file"}), 500

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting EPD Server")
    logger.info("=" * 60)

    # Avvia il worker thread per l'aggiornamento del display
    logger.info("Avvio worker thread per aggiornamento display...")
    worker_thread = threading.Thread(target=display_worker, daemon=True)
    worker_thread.start()
    logger.info("Worker thread avviato con successo")

    # Mostra la schermata di status iniziale (tramite coda)
    from utils import get_ip
    from templates.status import template_status

    # Ricavo la data attuale per la schermata di status
    from datetime import datetime
    now = datetime.now()

    status_data = {
        "system_name": now.strftime("%d.%m.%Y"),
        "status": now.strftime("%H:%M"),
        "field1_label": "IP",
        "field1_value": get_ip(),
        "field2_label": "Port",
        "field2_value": "5000",
        "field3_label": "Status",
        "field3_value": "Running",
        "icon": "WIFI.bmp"
    }

    logger.info("Generazione schermata di status iniziale...")
    status_img = template_status(status_data, epd.WIDTH, epd.HEIGHT)
    display_queue.put((status_img, "server_status", status_data))
    logger.info("Schermata di status aggiunta alla coda")

    logger.info(f"Avvio server Flask su http://127.0.0.1:5000")
    logger.info(f"Templates disponibili: {list(TEMPLATES.keys())}")
    logger.info("=" * 60)

    app.run(host="127.0.0.1", port=5000)
