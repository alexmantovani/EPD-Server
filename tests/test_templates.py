import pytest
from PIL import Image
from unittest.mock import Mock, patch

from templates.status import template_status
from templates.warning import template_warning
from templates.alert import template_alert
from templates.success import template_success
from templates.info import template_info


class TestTemplateStatus:
    """Test per il template status"""

    def test_status_creates_image(self, epd_colors):
        """Test che il template crei un'immagine"""
        data = {
            "system_name": "TEST SYSTEM",
            "status": "ONLINE",
            "field1_label": "IP",
            "field1_value": "192.168.1.1"
        }

        img = template_status(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        assert img.size == (400, 168)

    def test_status_with_all_fields(self, epd_colors):
        """Test status con tutti i campi"""
        data = {
            "system_name": "EPD SERVER",
            "status": "ONLINE",
            "field1_label": "IP",
            "field1_value": "192.168.1.1",
            "field2_label": "Port",
            "field2_value": "5000",
            "field3_label": "Status",
            "field3_value": "Running"
        }

        img = template_status(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        assert img.size == (400, 168)

    @patch('templates.status.load_icon')
    def test_status_with_icon(self, mock_load_icon, epd_colors):
        """Test status con icona"""
        # Mock dell'icona
        mock_icon = Image.new('RGB', (72, 72), color=(255, 255, 255))
        mock_load_icon.return_value = mock_icon

        data = {
            "system_name": "TEST",
            "status": "ONLINE",
            "icon": "WIFI.bmp"
        }

        img = template_status(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        mock_load_icon.assert_called_once()

    @patch('templates.status.load_icon')
    def test_status_with_svg(self, mock_load_icon, epd_colors, sample_svg):
        """Test status con SVG inline"""
        mock_icon = Image.new('RGB', (72, 72), color=(255, 255, 255))
        mock_load_icon.return_value = mock_icon

        data = {
            "system_name": "TEST",
            "status": "ONLINE",
            "svg": sample_svg
        }

        img = template_status(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        # Verifica che load_icon sia stato chiamato con i dati SVG
        call_args = mock_load_icon.call_args
        assert call_args[0][2] == sample_svg  # svg_data parameter


class TestTemplateWarning:
    """Test per il template warning"""

    def test_warning_creates_image(self, epd_colors):
        """Test che il template crei un'immagine"""
        data = {
            "top_text": "WARNING",
            "line1": "Sistema in manutenzione",
            "line2": "Riprova più tardi"
        }

        img = template_warning(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        assert img.size == (400, 168)

    @patch('templates.warning.load_icon')
    def test_warning_with_icon(self, mock_load_icon, epd_colors):
        """Test warning con icona"""
        mock_icon = Image.new('RGBA', (72, 72), color=(255, 255, 255, 255))
        mock_load_icon.return_value = mock_icon

        data = {
            "top_text": "WARNING",
            "icon": "WARNING.bmp",
            "line1": "Test line 1",
            "line2": "Test line 2"
        }

        img = template_warning(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        mock_load_icon.assert_called_once()


class TestTemplateAlert:
    """Test per il template alert"""

    def test_alert_creates_image(self, epd_colors):
        """Test che il template crei un'immagine"""
        data = {
            "title": "ALERT",
            "subtitle": "Attenzione",
            "line1": "Errore critico",
            "line2": "Contattare assistenza"
        }

        img = template_alert(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        assert img.size == (400, 168)

    @patch('templates.alert.load_icon')
    def test_alert_with_icon(self, mock_load_icon, epd_colors):
        """Test alert con icona"""
        mock_icon = Image.new('RGBA', (72, 72), color=(255, 255, 255, 255))
        mock_load_icon.return_value = mock_icon

        data = {
            "title": "ALERT",
            "icon": "ALERT.bmp",
            "line1": "Test"
        }

        img = template_alert(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        mock_load_icon.assert_called_once()

    def test_alert_multiple_lines(self, epd_colors):
        """Test alert con linee multiple"""
        data = {
            "title": "ALERT",
            "subtitle": "Subtitle",
            "line1": "Line 1",
            "line2": "Line 2",
            "line3": "Line 3"
        }

        img = template_alert(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)


class TestTemplateSuccess:
    """Test per il template success"""

    def test_success_creates_image(self, epd_colors):
        """Test che il template crei un'immagine"""
        data = {
            "title": "SUCCESS",
            "message": "Operazione completata"
        }

        img = template_success(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        assert img.size == (400, 168)

    @patch('templates.success.load_icon')
    def test_success_with_icon(self, mock_load_icon, epd_colors):
        """Test success con icona"""
        mock_icon = Image.new('RGBA', (72, 72), color=(255, 255, 255, 255))
        mock_load_icon.return_value = mock_icon

        data = {
            "title": "SUCCESS",
            "message": "Done",
            "icon": "CHECK.bmp"
        }

        img = template_success(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        mock_load_icon.assert_called_once()


class TestTemplateInfo:
    """Test per il template info"""

    def test_info_creates_image(self, epd_colors):
        """Test che il template crei un'immagine"""
        data = {
            "title": "INFORMATION",
            "line1": "Info line 1",
            "line2": "Info line 2"
        }

        img = template_info(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        assert img.size == (400, 168)

    @patch('templates.info.load_icon')
    def test_info_with_icon(self, mock_load_icon, epd_colors):
        """Test info con icona"""
        mock_icon = Image.new('RGBA', (72, 72), color=(255, 255, 255, 255))
        mock_load_icon.return_value = mock_icon

        data = {
            "title": "INFO",
            "icon": "INFO.bmp",
            "line1": "Test line"
        }

        img = template_info(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
        mock_load_icon.assert_called_once()

    def test_info_filters_empty_lines(self, epd_colors):
        """Test che le linee vuote vengano filtrate"""
        data = {
            "title": "INFO",
            "line1": "First line",
            "line2": "",
            "line3": "Third line"
        }

        img = template_info(data, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)


class TestTemplateDefaults:
    """Test per i valori di default dei template"""

    def test_status_default_values(self, epd_colors):
        """Test valori di default per status"""
        img = template_status({}, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)

    def test_warning_default_values(self, epd_colors):
        """Test valori di default per warning"""
        img = template_warning({}, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)

    def test_alert_default_values(self, epd_colors):
        """Test valori di default per alert"""
        img = template_alert({}, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)

    def test_success_default_values(self, epd_colors):
        """Test valori di default per success"""
        img = template_success({}, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)

    def test_info_default_values(self, epd_colors):
        """Test valori di default per info"""
        img = template_info({}, 400, 168, epd_colors)

        assert isinstance(img, Image.Image)
