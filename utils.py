import socket

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
