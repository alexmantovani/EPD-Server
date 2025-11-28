import os
from PIL import ImageFont

PICDIR = "pic"
LIBDIR = "lib"

FONT_BIG = ImageFont.truetype(os.path.join(PICDIR, 'Font.ttc'), 40)
FONT_SMALL = ImageFont.truetype(os.path.join(PICDIR, 'Font.ttc'), 24)

COLOR_MAP = {
    "white": (255,255,255),
    "black": (0,0,0),
    "red": (255,0,0),
    "yellow": (255,255,0)
}
