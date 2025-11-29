from PIL import Image, ImageDraw
from config import FONT_BIG, FONT_SMALL
from utils import bbox, load_icon

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
    icon_img = load_icon(icon, BLACK, data.get("svg"))
    if icon_img:
        bw, bh = icon_img.size
        img.paste(icon_img, ((WIDTH - bw) // 2, 100), icon_img if icon_img.mode == 'RGBA' else None)

    # Messaggio
    m_w, m_h = bbox(FONT_SMALL, message)
    draw.text(((WIDTH - m_w) // 2, HEIGHT - 60), message, fill=BLACK, font=FONT_SMALL)

    return img
