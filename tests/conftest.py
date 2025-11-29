import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# Aggiungi il path del progetto (directory parent di tests/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def mock_epd():
    """Mock del display EPD"""
    mock = Mock()
    mock.WHITE = (255, 255, 255)
    mock.BLACK = (0, 0, 0)
    mock.RED = (255, 0, 0)
    mock.YELLOW = (255, 255, 0)
    mock.init = Mock()
    mock.Clear = Mock()
    mock.display = Mock()
    mock.getbuffer = Mock(return_value=b'')
    mock.height = 168
    mock.width = 400
    return mock

@pytest.fixture
def app(monkeypatch, mock_epd):
    """Fixture per l'app Flask con EPD mockato"""
    # Mock EPDManager prima dell'import
    mock_epd_manager = Mock()
    mock_epd_manager.epd = mock_epd
    mock_epd_manager.WIDTH = 400
    mock_epd_manager.HEIGHT = 168
    mock_epd_manager.show = Mock()
    mock_epd_manager.show_server_status = Mock()

    # Patch EPDManager
    monkeypatch.setattr("server.EPDManager", lambda: mock_epd_manager)

    # Importa server dopo il patch
    import server
    server.app.config['TESTING'] = True

    # Non avviare il worker thread durante i test
    return server.app

@pytest.fixture
def client(app):
    """Client di test Flask"""
    return app.test_client()

@pytest.fixture
def epd_colors():
    """Fixture per i colori EPD"""
    return {
        "WHITE": (255, 255, 255),
        "BLACK": (0, 0, 0),
        "RED": (255, 0, 0),
        "YELLOW": (255, 255, 0)
    }

@pytest.fixture
def sample_svg():
    """SVG di esempio per i test"""
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="black"/>
    </svg>'''
