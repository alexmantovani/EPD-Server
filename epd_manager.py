import sys, os

LIBDIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if os.path.exists(LIBDIR):
    sys.path.append(LIBDIR)

from waveshare_epd import epd3in0g
from config import LIBDIR, PICDIR
from utils import get_ip
from templates.status import template_status
from logger import get_logger

if os.path.exists(LIBDIR):
    sys.path.append(LIBDIR)

logger = get_logger('epd_manager')


class EPDManager:
    def __init__(self):
        logger.info("Inizializzazione EPD Manager...")
        logger.debug("Caricamento driver EPD3IN0G")

        try:
            self.epd = epd3in0g.EPD()
            logger.debug("Driver EPD caricato con successo")

            logger.debug("Inizializzazione hardware EPD...")
            self.epd.init()
            logger.debug("Hardware EPD inizializzato")

            logger.debug("Pulizia display...")
            self.epd.Clear()
            logger.debug("Display pulito")

            self.WIDTH = self.epd.height
            self.HEIGHT = self.epd.width

            logger.info(f"EPD Manager inizializzato con successo (dimensioni: {self.WIDTH}x{self.HEIGHT})")

        except Exception as e:
            logger.error(f"Errore durante l'inizializzazione EPD Manager: {e}", exc_info=True)
            raise

    def show(self, image):
        """Mostra immagine sul display"""
        logger.debug(f"Richiesta visualizzazione immagine: {image.size}, mode: {image.mode}")

        try:
            buffer = self.epd.getbuffer(image)
            logger.debug(f"Buffer immagine creato (size: {len(buffer)} bytes)")

            logger.debug("Invio buffer al display...")
            self.epd.display(buffer)
            logger.debug("Immagine visualizzata con successo sul display")

        except Exception as e:
            logger.error(f"Errore durante la visualizzazione dell'immagine: {e}", exc_info=True)
            raise

    def show_server_status(self):
        """Schermata iniziale"""
        logger.info("Generazione schermata di status del server...")

        data = {
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

        logger.debug(f"Dati status: {data}")

        try:
            img = template_status(data, self.WIDTH, self.HEIGHT)
            logger.debug("Template status generato con successo")

            self.show(img)
            logger.info("Schermata di status visualizzata")

        except Exception as e:
            logger.error(f"Errore durante la generazione/visualizzazione della schermata di status: {e}", exc_info=True)
            raise
