from PIL import Image, ImageDraw
from config import PICDIR, FONT_BIG, FONT_SMALL
from utils import bbox, svg_to_image
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

    # Icona (supporta sia BMP che SVG)
    svg_data = data.get("svg", None)
    if svg_data:
        # Se c'è un SVG, usalo e coloralo di nero (colore del testo)
        icon_img = svg_to_image(svg_data, BLACK)
        bw, bh = icon_img.size
        img.paste(icon_img, ((WIDTH - bw) // 2, 100), icon_img if icon_img.mode == 'RGBA' else None)
    else:
        # Altrimenti usa l'icona BMP tradizionale
        path = os.path.join(PICDIR, icon)
        if os.path.exists(path):
            bmp = Image.open(path)
            bw, bh = bmp.size
            img.paste(bmp, ((WIDTH - bw) // 2, 100))

    # Messaggio
    m_w, m_h = bbox(FONT_SMALL, message)
    draw.text(((WIDTH - m_w) // 2, HEIGHT - 60), message, fill=BLACK, font=FONT_SMALL)

    return img
