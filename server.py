from flask import Flask, request, jsonify
import logging, time

from epd_manager import EPDManager
from templates import TEMPLATES

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

epd = EPDManager()

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

    epd.show(img)
    time.sleep(1)

    return jsonify({"status": "OK", "template": name})

if __name__ == "__main__":
    logging.info("Starting EPD Server…")
    epd.show_server_status()
    app.run(host="0.0.0.0", port=5000)
