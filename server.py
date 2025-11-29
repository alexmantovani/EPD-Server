from flask import Flask, request, jsonify
import logging, time
import threading
import queue
import os
from werkzeug.utils import secure_filename

from epd_manager import EPDManager
from templates import TEMPLATES
from config import PICDIR

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

    logging.info("Display worker thread avviato")
    while True:
        try:
            # Attende un'immagine dalla coda (bloccante)
            img, template_name, data = display_queue.get()

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
                logging.info(f"Saltate {skipped} richieste intermedie, processo solo l'ultima: {template_name}")

            # Calcola il tempo trascorso dall'ultimo aggiornamento
            elapsed = time.time() - last_update_time

            # Se non sono passati almeno MIN_UPDATE_INTERVAL secondi, aspetta
            if elapsed < MIN_UPDATE_INTERVAL:
                wait_time = MIN_UPDATE_INTERVAL - elapsed
                logging.info(f"Attendo {wait_time:.1f}s prima del prossimo aggiornamento (ultimo: {elapsed:.1f}s fa)")
                time.sleep(wait_time)

            logging.info(f"Aggiornamento display con template: {template_name}")
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
            logging.info("Display aggiornato con successo")
        except Exception as e:
            logging.error(f"Errore nell'aggiornamento del display: {e}")
            current_display_state["status"] = "error"
            display_queue.task_done()

@app.route("/update", methods=["POST"])
def update_display():
    data = request.json
    name = data.get("template", "warning")

    if name not in TEMPLATES:
        return jsonify({"error": "Template non valido"}), 400

    template = TEMPLATES[name]

    # genera immagine
    img = template(
        data,
        epd.WIDTH,
        epd.HEIGHT,
        epd_colors={"WHITE": epd.epd.WHITE, "BLACK": epd.epd.BLACK,
                    "RED": epd.epd.RED, "YELLOW": epd.epd.YELLOW}
    )

    # Aggiungi l'immagine alla coda invece di bloccare
    try:
        display_queue.put((img, name, data), timeout=2)
        logging.info(f"Immagine '{name}' aggiunta alla coda (dimensione: {display_queue.qsize()})")
        return jsonify({"status": "OK", "template": name, "queued": True})
    except queue.Full:
        logging.warning("Coda display piena, richiesta rifiutata")
        return jsonify({"error": "Display occupato, riprova tra poco"}), 503

@app.route("/status", methods=["GET"])
def get_display_status():
    """Restituisce lo stato corrente del display"""
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

    return jsonify(response)

def allowed_file(filename):
    """Verifica se l'estensione del file è consentita"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_image():
    """Carica un'immagine nella cartella pic/"""
    # Verifica che ci sia un file nella richiesta
    if 'file' not in request.files:
        return jsonify({"error": "Nessun file fornito"}), 400

    file = request.files['file']

    # Verifica che sia stato selezionato un file
    if file.filename == '':
        return jsonify({"error": "Nessun file selezionato"}), 400

    # Verifica l'estensione del file
    if not allowed_file(file.filename):
        return jsonify({
            "error": "Tipo file non consentito",
            "allowed_extensions": list(ALLOWED_EXTENSIONS)
        }), 400

    # Verifica la dimensione del file
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_FILE_SIZE:
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

    # Salva il file
    filepath = os.path.join(PICDIR, filename)

    try:
        file.save(filepath)
        logging.info(f"File salvato: {filepath} ({file_size} bytes)")

        return jsonify({
            "status": "OK",
            "filename": filename,
            "path": filepath,
            "size_bytes": file_size
        }), 201

    except Exception as e:
        logging.error(f"Errore durante il salvataggio del file: {e}")
        return jsonify({"error": "Errore durante il salvataggio del file"}), 500

if __name__ == "__main__":
    logging.info("Starting EPD Server…")

    # Avvia il worker thread per l'aggiornamento del display
    worker_thread = threading.Thread(target=display_worker, daemon=True)
    worker_thread.start()
    logging.info("Worker thread avviato")

    # Mostra la schermata di status iniziale (tramite coda)
    from utils import get_ip
    from templates.status import template_status

    status_data = {
        "system_name": "EPD SERVER",
        "status": "ONLINE",
        "field1_label": "IP",
        "field1_value": get_ip(),
        "field2_label": "Port",
        "field2_value": "5000",
        "field3_label": "Status",
        "field3_value": "Running",
        "icon": "WIFI.bmp"
    }

    status_img = template_status(status_data, epd.WIDTH, epd.HEIGHT)
    display_queue.put((status_img, "server_status", status_data))

    app.run(host="127.0.0.1", port=5000)
