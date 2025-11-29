from PIL import Image, ImageDraw
from config import FONT_BIG, FONT_SMALL
from utils import bbox, load_icon

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

    # Icona
    icon_img = load_icon(icon, WHITE, data.get("svg"))
    if icon_img:
        bw, bh = icon_img.size
        y = top_h + (HEIGHT - top_h - bh) // 2
        img.paste(icon_img, (20, y), icon_img if icon_img.mode == 'RGBA' else None)
        draw.text((20 + bw + 20, y), line1, fill=WHITE, font=FONT_SMALL)
        draw.text((20 + bw + 20, y + 30), line2, fill=WHITE, font=FONT_SMALL)

    return img
