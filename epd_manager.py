import sys, os, logging
from waveshare_epd import epd3in0g
from config import LIBDIR, PICDIR
from utils import get_ip
from templates.status import template_status

if os.path.exists(LIBDIR):
    sys.path.append(LIBDIR)

class EPDManager:
    def __init__(self):
        self.epd = epd3in0g.EPD()
        self.epd.init()
        self.epd.Clear()
        self.WIDTH = self.epd.height
        self.HEIGHT = self.epd.width

    def show(self, image):
        """Mostra immagine sul display"""
        self.epd.display(self.epd.getbuffer(image))

    def show_server_status(self):
        """Schermata iniziale"""
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

        img = template_status(data, self.WIDTH, self.HEIGHT)
        self.show(img)
