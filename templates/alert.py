from PIL import Image, ImageDraw
from config import FONT_BIG, FONT_SMALL
from utils import bbox, load_icon

def template_alert(data, WIDTH, HEIGHT, epd_colors):
    YELLOW = epd_colors["YELLOW"]
    RED    = epd_colors["RED"]
    BLACK  = epd_colors["BLACK"]

    img = Image.new("RGB", (WIDTH, HEIGHT), YELLOW)
    draw = ImageDraw.Draw(img)

    title = data.get("title", "ALERT")
    icon = data.get("icon", "ALERT.bmp")

    lines = [
        data.get("subtitle", ""),
        data.get("line1", ""), 
        data.get("line2", ""), 
        data.get("line3", "")
    ]
    active = [l for l in lines if l]

    # Header rosso
    header_h = 45
    draw.rectangle((0, 0, WIDTH, header_h), fill=RED)
    t_w, t_h = bbox(FONT_BIG, title)
    draw.text(((WIDTH - t_w) // 2, (header_h - t_h) // 2), title, fill=BLACK, font=FONT_BIG)

    # Icona
    icon_w = 0
    icon_img = load_icon(icon, BLACK, data.get("svg"))
    if icon_img:
        bw, bh = icon_img.size
        icon_w = bw
        y = header_h + (HEIGHT - header_h - bh) // 2
        img.paste(icon_img, (20, y), icon_img if icon_img.mode == 'RGBA' else None)

    # Testo centrato verticalmente
    line_spacing = 28
    total_h = len(active)*24 + (len(active)-1)*(line_spacing-24)
    y = header_h + (HEIGHT - header_h - total_h)//2
    x = 20 + icon_w + (20 if icon_w else 0)

    for line in active:
        draw.text((x, y), line, fill=BLACK, font=FONT_SMALL)
        y += line_spacing

    return img
