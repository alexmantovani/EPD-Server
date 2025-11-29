from PIL import Image, ImageDraw
from config import FONT_BIG, FONT_SMALL
from utils import bbox, load_icon

def template_status(data, WIDTH, HEIGHT, epd_colors=None):
    epd_colors = epd_colors or {}
    WHITE = epd_colors.get("WHITE", (255,255,255))
    BLACK = epd_colors.get("BLACK", (0,0,0))
    RED = epd_colors.get("RED", (255,0,0))
    YELLOW = epd_colors.get("YELLOW", (255,255,0))

    img = Image.new("RGB", (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    system = data.get("system_name", "SYSTEM")
    status = data.get("status", "ONLINE")
    color = BLACK if status == "ONLINE" else RED

    icon = data.get("icon", "STATUS.bmp")

    f1l = data.get("field1_label", "")
    f1v = data.get("field1_value", "")
    f2l = data.get("field2_label", "")
    f2v = data.get("field2_value", "")
    f3l = data.get("field3_label", "")
    f3v = data.get("field3_value", "")

    # Header
    header_h = 45
    draw.rectangle((0, 0, WIDTH, header_h), fill=BLACK)
    draw.text((20, 0), system, fill=WHITE, font=FONT_BIG)

    # badge status
    badge_h = 30
    draw.rectangle((WIDTH-130, 4, WIDTH-20, 4+badge_h), fill=color)
    s_w, s_h = bbox(FONT_SMALL, status)
    draw.text((WIDTH-75 - s_w//2, 4+5), status, fill=WHITE, font=FONT_SMALL)

    # Icona
    icon_img = load_icon(icon, color, data.get("svg"))
    if icon_img:
        img.paste(icon_img, (20, header_h + 26), icon_img if icon_img.mode == 'RGBA' else None)

    # Campi dati
    x_label = 115
    y_base = header_h + 20
    spacing = 28

    labels = [f1l, f2l, f3l]
    max_label = max([bbox(FONT_SMALL, l+":")[0] for l in labels if l] + [0])
    x_value = x_label + max_label + 10

    if f1l:
        draw.text((x_label, y_base), f1l+":", fill=BLACK, font=FONT_SMALL)
        draw.text((x_value, y_base), f1v, fill=BLACK, font=FONT_SMALL)

    if f2l:
        draw.text((x_label, y_base+spacing), f2l+":", fill=BLACK, font=FONT_SMALL)
        draw.text((x_value, y_base+spacing), f2v, fill=BLACK, font=FONT_SMALL)

    if f3l:
        draw.text((x_label, y_base+2*spacing), f3l+":", fill=BLACK, font=FONT_SMALL)
        draw.text((x_value, y_base+2*spacing), f3v, fill=BLACK, font=FONT_SMALL)

    return img
