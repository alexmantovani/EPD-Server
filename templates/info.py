from PIL import Image, ImageDraw
from config import FONT_BIG, FONT_SMALL
from utils import bbox, load_icon

def template_info(data, WIDTH, HEIGHT, epd_colors):
    WHITE = epd_colors["WHITE"]
    BLACK = epd_colors["BLACK"]

    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    title = data.get("title", "INFORMATION")
    icon = data.get("icon", "INFO.bmp")
    lines = [data.get("line1", ""), data.get("line2", ""), data.get("line3", "")]
    active_lines = [l for l in lines if l]

    # Header
    top_h = 45
    draw.rectangle((0, 0, WIDTH, top_h), fill=BLACK)
    t_w, t_h = bbox(FONT_BIG, title)
    draw.text(((WIDTH - t_w) // 2, (top_h - t_h) // 2), title, fill=WHITE, font=FONT_BIG)

    # Icona
    icon_w = 0
    icon_img = load_icon(icon, BLACK, data.get("svg"))
    if icon_img:
        bw, bh = icon_img.size
        icon_w = bw
        y = top_h + (HEIGHT - top_h - bh) // 2
        img.paste(icon_img, (20, y), icon_img if icon_img.mode == 'RGBA' else None)

    # Testo
    if active_lines:
        line_spacing = 30
        total_h = len(active_lines) * 24 + (len(active_lines)-1)*(line_spacing-24)

        start_y = top_h + (HEIGHT - top_h - total_h) // 2
        x = 20 + icon_w + (20 if icon_w else 0)
        
        y = start_y
        for line in active_lines:
            draw.text((x, y), line, fill=BLACK, font=FONT_SMALL)
            y += line_spacing

    return img
