from PIL import Image, ImageDraw
from config import FONT_BIG, FONT_SMALL
from utils import bbox, load_icon
from logger import get_logger

logger = get_logger('templates.message')


def template_message(data, WIDTH, HEIGHT, epd_colors):
    """
    Template generico per messaggi con background, colore e icona personalizzabili.

    Args:
        data: {
            "background": "white|black|red|yellow" (optional, default: "white")
            "color": "white|black|red|yellow" (optional, auto-detected based on background)
            "title": "Titolo" (optional, default: "")
            "message": "Messaggio" (optional, default: "")
            "icon": "alert.bmp" (optional, no icon if not provided)
            "svg": "inline SVG" (optional)
        }
        WIDTH: Display width (400px)
        HEIGHT: Display height (168px)
        epd_colors: Color dictionary (WHITE, BLACK, RED, YELLOW)

    Returns:
        PIL.Image.Image: 400x168 RGB image
    """
    logger.debug(f"template_message chiamato con dimensioni {WIDTH}x{HEIGHT}")

    # Estrai parametri
    bg_name = data.get("background", "white")
    color_name = data.get("color", None)
    title = data.get("title", "")
    message = data.get("message", "")
    icon_filename = data.get("icon", None)

    logger.debug(f"Parametri: bg={bg_name}, color={color_name}, title='{title}', message='{message}', icon={icon_filename}")

    # Ottieni colore background
    bg = epd_colors.get(bg_name.upper(), epd_colors["WHITE"])

    # Colore testo automatico se non specificato
    if color_name:
        text_color = epd_colors.get(color_name.upper(), epd_colors["BLACK"])
        logger.debug(f"Colore testo specificato: {color_name}")
    else:
        # Contrasto automatico: bianco su nero, nero su tutto il resto
        text_color = epd_colors["WHITE"] if bg == epd_colors["BLACK"] else epd_colors["BLACK"]
        logger.debug(f"Colore testo automatico: {'white' if text_color == epd_colors['WHITE'] else 'black'}")

    # Crea immagine
    img = Image.new("RGB", (WIDTH, HEIGHT), bg)
    draw = ImageDraw.Draw(img)
    logger.debug("Canvas immagine creato")

    # Carica icona se presente
    icon_img = None
    icon_width = 0
    if icon_filename:
        logger.debug(f"Caricamento icona: {icon_filename}")
        try:
            icon_img = load_icon(icon_filename, text_color, data.get("svg"))
            if icon_img:
                icon_width = icon_img.size[0]
                logger.debug(f"Icona caricata: {icon_img.size}")
            else:
                logger.warning(f"Icona non caricata: {icon_filename}")
        except Exception as e:
            logger.error(f"Errore nel caricamento icona '{icon_filename}': {e}", exc_info=True)

    # Calcola posizione X per il testo
    # Se c'è un'icona, il testo va a destra dell'icona
    # Se non c'è icona, il testo è centrato
    if icon_img:
        # Posiziona icona a sinistra
        icon_x = 20
        icon_y = (HEIGHT - icon_img.size[1]) // 2
        img.paste(icon_img, (icon_x, icon_y), icon_img if icon_img.mode == 'RGBA' else None)

        # Testo a destra dell'icona
        text_x = icon_x + icon_width + 20
        text_max_width = WIDTH - text_x - 20
    else:
        # Testo centrato
        text_x = None  # Sarà calcolato per centrare
        text_max_width = WIDTH - 40

    # Renderizza titolo
    title_y = HEIGHT // 3
    if title:
        t_w, t_h = bbox(FONT_BIG, title)
        if icon_img:
            # Allineato a sinistra accanto all'icona
            draw.text((text_x, title_y - t_h), title, fill=text_color, font=FONT_BIG)
        else:
            # Centrato
            draw.text(((WIDTH - t_w) // 2, title_y - t_h), title, fill=text_color, font=FONT_BIG)

    # Renderizza messaggio
    message_y = HEIGHT // 2
    if message:
        m_w, m_h = bbox(FONT_SMALL, message)
        if icon_img:
            # Allineato a sinistra accanto all'icona
            draw.text((text_x, message_y), message, fill=text_color, font=FONT_SMALL)
            logger.debug(f"Messaggio renderizzato (allineato a destra icona): '{message[:30]}...'")
        else:
            # Centrato
            draw.text(((WIDTH - m_w) // 2, message_y), message, fill=text_color, font=FONT_SMALL)
            logger.debug(f"Messaggio renderizzato (centrato): '{message[:30]}...'")

    logger.info(f"Template message generato con successo ({WIDTH}x{HEIGHT}, bg={bg_name}, icon={'sì' if icon_img else 'no'})")
    return img
