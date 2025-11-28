from PIL import Image, ImageDraw
from config import PICDIR, FONT_BIG, FONT_SMALL
from utils import bbox
import os

def template_success(data, WIDTH, HEIGHT, epd_colors):
    WHITE = epd_colors["WHITE"]
    BLACK = epd_colors["BLACK"]

    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    title = data.get("title", "SUCCESS")
    message = data.get("message", "")
    icon = data.get("icon", "CHECK.bmp")

    # Header
    header_h = 70
    draw.rectangle((0, 0, WIDTH, header_h), fill=BLACK)
    t_w, t_h = bbox(FONT_BIG, title)
    draw.text(((WIDTH - t_w) // 2, (header_h - t_h) // 2), title, fill=WHITE, font=FONT_BIG)

    # Icona
    path = os.path.join(PICDIR, icon)
    if os.path.exists(path):
        bmp = Image.open(path)
        bw, bh = bmp.size
        img.paste(bmp, ((WIDTH - bw) // 2, 100))

    # Messaggio
    m_w, m_h = bbox(FONT_SMALL, message)
    draw.text(((WIDTH - m_w) // 2, HEIGHT - 60), message, fill=BLACK, font=FONT_SMALL)

    return img
