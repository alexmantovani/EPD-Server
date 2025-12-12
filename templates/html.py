from PIL import Image
from io import BytesIO
from weasyprint import HTML


def template_html(data, WIDTH, HEIGHT, epd_colors):
    """
    Render raw HTML content as display image.

    Args:
        data: {
            "html": "<html>...</html>",  # Raw HTML string (required)
            "bg_color": "white|black|red|yellow" (optional, default: "white")
        }
        WIDTH: Display width (400px)
        HEIGHT: Display height (168px)
        epd_colors: Color dictionary (WHITE, BLACK, RED, YELLOW)

    Returns:
        PIL.Image.Image: 400x168 RGB image
    """
    # Extract HTML content
    html_content = data.get("html", "<html><body><p>No HTML content provided</p></body></html>")

    # Get background color (if needed for fallback)
    bg_color_name = data.get("bg_color", "white")
    bg_color = epd_colors.get(bg_color_name.upper(), epd_colors["WHITE"])

    # Create HTML document with inline CSS to set viewport size
    # This ensures proper scaling for the EPD display
    html_with_viewport = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: {WIDTH}px {HEIGHT}px;
                margin: 0;
            }}
            body {{
                margin: 0;
                padding: 0;
                width: {WIDTH}px;
                height: {HEIGHT}px;
                overflow: hidden;
            }}
        </style>
    </head>
    <body>
        {html_content if not html_content.strip().startswith('<!DOCTYPE') and not html_content.strip().startswith('<html') else ''}
    </body>
    </html>
    """

    # If the HTML already has full structure, use it as-is
    if html_content.strip().startswith('<!DOCTYPE') or html_content.strip().startswith('<html'):
        html_with_viewport = html_content

    try:
        # Create HTML document from string
        html_doc = HTML(string=html_with_viewport)

        # Render to PNG in memory
        png_bytes = BytesIO()
        html_doc.write_png(png_bytes)
        png_bytes.seek(0)

        # Open with PIL
        img = Image.open(png_bytes)

        # Resize to exact display dimensions
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

        # Ensure RGB mode for EPD display
        if img.mode != 'RGB':
            img = img.convert('RGB')

        return img

    except Exception as e:
        # Fallback: create error image if HTML rendering fails
        img = Image.new("RGB", (WIDTH, HEIGHT), bg_color)
        from PIL import ImageDraw
        from config import FONT_SMALL

        draw = ImageDraw.Draw(img)
        error_msg = f"HTML rendering error: {str(e)[:50]}"
        text_color = epd_colors["BLACK"] if bg_color_name == "white" else epd_colors["WHITE"]

        draw.text((10, HEIGHT//2 - 12), error_msg, fill=text_color, font=FONT_SMALL)

        return img
