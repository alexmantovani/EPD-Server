from flask import Flask, request, jsonify
import logging, time
import threading
import queue

from epd_manager import EPDManager
from templates import TEMPLATES

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

epd = EPDManager()

# Coda thread-safe per le immagini da visualizzare
display_queue = queue.Queue(maxsize=10)

# Intervallo minimo tra aggiornamenti del display (in secondi)
MIN_UPDATE_INTERVAL = 10
last_update_time = 0

def display_worker():
    """Worker thread che consuma la coda e aggiorna il display"""
    global last_update_time

    logging.info("Display worker thread avviato")
    while True:
        try:
            # Attende un'immagine dalla coda (bloccante)
            img, template_name = display_queue.get()

            # Se ci sono altre immagini in coda, prendi solo l'ultima (scarta quelle intermedie)
            skipped = 0
            while not display_queue.empty():
                try:
                    display_queue.task_done()  # Marca come completata quella che stiamo scartando
                    img, template_name = display_queue.get_nowait()
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

            display_queue.task_done()
            logging.info("Display aggiornato con successo")
        except Exception as e:
            logging.error(f"Errore nell'aggiornamento del display: {e}")
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
        display_queue.put((img, name), timeout=2)
        logging.info(f"Immagine '{name}' aggiunta alla coda (dimensione: {display_queue.qsize()})")
        return jsonify({"status": "OK", "template": name, "queued": True})
    except queue.Full:
        logging.warning("Coda display piena, richiesta rifiutata")
        return jsonify({"error": "Display occupato, riprova tra poco"}), 503

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
    display_queue.put((status_img, "server_status"))

    app.run(host="0.0.0.0", port=5000)
