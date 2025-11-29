import pytest
from unittest.mock import Mock, patch, mock_open
from PIL import Image
import os

from utils import bbox, load_icon, svg_to_image, get_ip


class TestBbox:
    """Test per la funzione bbox"""

    def test_bbox_returns_width_and_height(self):
        """Test che bbox restituisca larghezza e altezza"""
        mock_font = Mock()
        mock_font.getbbox.return_value = (0, 0, 100, 50)

        width, height = bbox(mock_font, "test text")

        assert width == 100
        assert height == 50
        mock_font.getbbox.assert_called_once_with("test text")


class TestGetIP:
    """Test per la funzione get_ip"""

    def test_get_ip_success(self):
        """Test get_ip quando la connessione riesce"""
        with patch('socket.socket') as mock_socket:
            mock_sock_instance = Mock()
            mock_sock_instance.getsockname.return_value = ('192.168.1.100', 0)
            mock_socket.return_value = mock_sock_instance

            ip = get_ip()

            assert ip == '192.168.1.100'
            mock_sock_instance.connect.assert_called_once_with(("8.8.8.8", 80))
            mock_sock_instance.close.assert_called_once()

    def test_get_ip_failure(self):
        """Test get_ip quando la connessione fallisce"""
        with patch('socket.socket', side_effect=Exception("Connection failed")):
            ip = get_ip()
            assert ip == "N/A"


class TestSvgToImage:
    """Test per la funzione svg_to_image"""

    def test_svg_to_image_with_rgb_color(self, sample_svg):
        """Test conversione SVG con colore RGB"""
        color = (255, 0, 0)  # Rosso

        img = svg_to_image(sample_svg, color)

        assert isinstance(img, Image.Image)
        assert img.size == (72, 72)

    def test_svg_to_image_with_int_color(self, sample_svg):
        """Test conversione SVG con colore intero (EPD format)"""
        # EPD usa formato BGR come intero
        color = 0x0000FF  # Rosso in formato BGR

        img = svg_to_image(sample_svg, color)

        assert isinstance(img, Image.Image)
        assert img.size == (72, 72)

    def test_svg_color_replacement(self, sample_svg):
        """Test che i colori nell'SVG vengano sostituiti"""
        color = (0, 255, 0)  # Verde

        img = svg_to_image(sample_svg, color)

        # Verifica che l'immagine sia stata creata
        assert isinstance(img, Image.Image)

    def test_svg_with_currentcolor(self):
        """Test SVG con currentColor"""
        svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72">
            <rect fill="currentColor" width="72" height="72"/>
        </svg>'''

        color = (255, 0, 0)
        img = svg_to_image(svg, color)

        assert isinstance(img, Image.Image)


class TestLoadIcon:
    """Test per la funzione load_icon"""

    def test_load_icon_with_svg_data(self, sample_svg):
        """Test caricamento icona da dati SVG inline"""
        color = (0, 0, 0)

        img = load_icon("dummy.svg", color, svg_data=sample_svg)

        assert img is not None
        assert isinstance(img, Image.Image)

    def test_load_icon_from_svg_file(self, sample_svg, tmp_path):
        """Test caricamento icona da file SVG"""
        # Crea file SVG temporaneo
        svg_file = tmp_path / "test.svg"
        svg_file.write_text(sample_svg)

        with patch('config.PICDIR', str(tmp_path)):
            color = (0, 0, 0)
            img = load_icon("test.svg", color)

            assert img is not None
            assert isinstance(img, Image.Image)
            assert img.size == (72, 72)

    def test_load_icon_from_bmp_file(self, tmp_path):
        """Test caricamento icona da file BMP"""
        # Crea un'immagine BMP temporanea
        bmp_file = tmp_path / "test.bmp"
        test_img = Image.new('RGB', (72, 72), color=(255, 255, 255))
        test_img.save(str(bmp_file))

        with patch('config.PICDIR', str(tmp_path)):
            color = (0, 0, 0)
            img = load_icon("test.bmp", color)

            assert img is not None
            assert isinstance(img, Image.Image)
            assert img.size == (72, 72)

    def test_load_icon_from_png_file(self, tmp_path):
        """Test caricamento icona da file PNG"""
        # Crea un'immagine PNG temporanea
        png_file = tmp_path / "test.png"
        test_img = Image.new('RGB', (72, 72), color=(255, 255, 255))
        test_img.save(str(png_file))

        with patch('config.PICDIR', str(tmp_path)):
            color = (0, 0, 0)
            img = load_icon("test.png", color)

            assert img is not None
            assert isinstance(img, Image.Image)
            assert img.size == (72, 72)

    def test_load_icon_file_not_found(self, tmp_path):
        """Test quando il file non esiste"""
        with patch('config.PICDIR', str(tmp_path)):
            color = (0, 0, 0)
            img = load_icon("nonexistent.png", color)

            assert img is None

    def test_load_icon_svg_data_takes_precedence(self, sample_svg, tmp_path):
        """Test che svg_data abbia precedenza sul file"""
        # Anche se esiste un file, svg_data dovrebbe essere usato
        color = (0, 0, 0)

        img = load_icon("ignored.png", color, svg_data=sample_svg)

        assert img is not None
        assert isinstance(img, Image.Image)
        # Non dovrebbe cercare di aprire il file

    def test_load_icon_colorizes_svg(self, sample_svg):
        """Test che gli SVG vengano colorati correttamente"""
        red_color = (255, 0, 0)
        blue_color = (0, 0, 255)

        red_img = load_icon("test.svg", red_color, svg_data=sample_svg)
        blue_img = load_icon("test.svg", blue_color, svg_data=sample_svg)

        # Entrambe le immagini dovrebbero essere create
        assert red_img is not None
        assert blue_img is not None

        # Le immagini dovrebbero essere diverse (colori diversi)
        # Nota: questo è un test base, potremmo fare controlli più sofisticati sui pixel
