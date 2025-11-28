import socket
import re
from io import BytesIO
from PIL import Image
import cairosvg

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "N/A"

def bbox(font, text):
    """Restituisce larghezza e altezza di un testo con un font"""
    b = font.getbbox(text)
    return b[2], b[3]

def svg_to_image(svg_string, color):
    """
    Converte una stringa SVG in un'immagine PIL, colorandola con il colore specificato.

    Args:
        svg_string: Stringa contenente l'SVG
        color: Tupla RGB (r, g, b) o intero EPD color per il colore dell'SVG

    Returns:
        PIL.Image: Immagine convertita dall'SVG
    """
    # Se color è un intero (EPD color code in formato BGR), convertiamolo in RGB
    if isinstance(color, int):
        # L'EPD usa formato BGR (Blue-Green-Red) come intero esadecimale
        # Estrai i componenti BGR e converti in RGB
        b = (color >> 16) & 0xFF
        g = (color >> 8) & 0xFF
        r = color & 0xFF
        color = (r, g, b)

    # Converti il colore RGB in formato hex
    color_hex = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])

    # Sostituisci i colori comuni nell'SVG con il colore desiderato
    # Supporta: currentColor, fill="black", fill="white", fill="#000", ecc.
    svg_colored = svg_string

    # Sostituisci currentColor
    svg_colored = re.sub(r'currentColor', color_hex, svg_colored, flags=re.IGNORECASE)

    # Sostituisci fill="black" o fill="#000" o fill="#000000"
    svg_colored = re.sub(
        r'fill\s*=\s*["\'](?:#000000|#000|black)["\']',
        f'fill="{color_hex}"',
        svg_colored,
        flags=re.IGNORECASE
    )

    # Sostituisci stroke se presente
    svg_colored = re.sub(
        r'stroke\s*=\s*["\'](?:#000000|#000|black)["\']',
        f'stroke="{color_hex}"',
        svg_colored,
        flags=re.IGNORECASE
    )

    # Se non ci sono attributi fill, aggiungi uno di default al root SVG
    if 'fill=' not in svg_colored:
        svg_colored = re.sub(
            r'<svg',
            f'<svg fill="{color_hex}"',
            svg_colored,
            count=1
        )

    # Converti SVG in PNG usando cairosvg
    png_data = cairosvg.svg2png(bytestring=svg_colored.encode('utf-8'))

    # Converti PNG in PIL Image
    img = Image.open(BytesIO(png_data))

    return img
