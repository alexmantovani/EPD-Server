from PIL import Image, ImageDraw
from config import COLOR_MAP, FONT_BIG, FONT_SMALL
from utils import bbox

def template_simple(data, WIDTH, HEIGHT, epd_colors):
    bg_name = data.get("bg_color", "white")
    color_name = data.get("color", None)

    bg = epd_colors.get(bg_name.upper(), epd_colors["WHITE"])

    # Colore testo automatico
    if color_name:
        text_color = epd_colors.get(color_name.upper(), epd_colors["BLACK"])
    else:
        text_color = epd_colors["BLACK"] if bg != epd_colors["BLACK"] else epd_colors["WHITE"]

    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(img)

    title = data.get("title", "")
    message = data.get("message", "")
    footer = data.get("footer", "")

    if title:
        t_w, t_h = bbox(FONT_BIG, title)
        draw.text(((WIDTH-t_w)//2, HEIGHT//3 - t_h), title, fill=text_color, font=FONT_BIG)

    if message:
        m_w, m_h = bbox(FONT_SMALL, message)
        draw.text(((WIDTH-m_w)//2, HEIGHT//2), message, fill=text_color, font=FONT_SMALL)

    if footer:
        f_w, f_h = bbox(FONT_SMALL, footer)
        draw.text(((WIDTH-f_w)//2, HEIGHT-50), footer, fill=text_color, font=FONT_SMALL)

    return img
