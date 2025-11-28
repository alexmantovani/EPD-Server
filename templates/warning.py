from PIL import Image, ImageDraw
from config import PICDIR, FONT_BIG, FONT_SMALL
from utils import bbox, svg_to_image
import os

def template_warning(data, WIDTH, HEIGHT, epd_colors=None):
    epd_colors = epd_colors or {}
    WHITE = epd_colors.get("WHITE")
    RED = epd_colors.get("RED")
    BLACK = epd_colors.get("BLACK")

    img = Image.new('RGB', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    top_text = data.get("top_text", "WARNING")
    icon = data.get("icon", "WARNING.bmp")
    line1 = data.get("line1", "")
    line2 = data.get("line2", "")

    # banda superiore
    top_h = HEIGHT // 4
    draw.rectangle((0, 0, WIDTH, top_h), fill=BLACK)

    t_w, t_h = bbox(FONT_BIG, top_text)
    draw.text(((WIDTH - t_w) // 2, (top_h - t_h) // 2), top_text, fill=WHITE, font=FONT_BIG)

    # area inferiori
    draw.rectangle((0, top_h, WIDTH, HEIGHT), fill=RED)

    # icona (supporta sia BMP che SVG)
    svg_data = data.get("svg", None)
    if svg_data:
        # Se c'è un SVG, usalo e coloralo di bianco (colore del testo)
        icon_img = svg_to_image(svg_data, WHITE)
        bw, bh = icon_img.size
        y = top_h + (HEIGHT - top_h - bh) // 2
        img.paste(icon_img, (20, y), icon_img if icon_img.mode == 'RGBA' else None)
        draw.text((20 + bw + 20, y), line1, fill=WHITE, font=FONT_SMALL)
        draw.text((20 + bw + 20, y + 30), line2, fill=WHITE, font=FONT_SMALL)
    else:
        # Altrimenti usa l'icona BMP tradizionale
        path = os.path.join(PICDIR, icon)
        if os.path.exists(path):
            bmp = Image.open(path)
            bw, bh = bmp.size
            y = top_h + (HEIGHT - top_h - bh) // 2
            img.paste(bmp, (20, y))
            draw.text((20 + bw + 20, y), line1, fill=WHITE, font=FONT_SMALL)
            draw.text((20 + bw + 20, y + 30), line2, fill=WHITE, font=FONT_SMALL)

    return img
