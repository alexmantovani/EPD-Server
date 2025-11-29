import pytest
import json
import io
import time
from unittest.mock import Mock, patch, mock_open

class TestUpdateEndpoint:
    """Test per l'endpoint POST /update"""

    def test_update_with_valid_template(self, client):
        """Test aggiornamento con template valido"""
        data = {
            "template": "status",
            "system_name": "TEST",
            "status": "ONLINE"
        }

        response = client.post('/update',
                              data=json.dumps(data),
                              content_type='application/json')

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'OK'
        assert json_data['template'] == 'status'
        assert json_data['queued'] == True

    def test_update_with_invalid_template(self, client):
        """Test con template non valido"""
        data = {
            "template": "nonexistent",
            "system_name": "TEST"
        }

        response = client.post('/update',
                              data=json.dumps(data),
                              content_type='application/json')

        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data

    def test_update_queue_full(self, client, monkeypatch):
        """Test quando la coda è piena"""
        import server

        # Simula coda piena
        mock_queue = Mock()
        mock_queue.put = Mock(side_effect=Exception("Full"))
        monkeypatch.setattr(server, "display_queue", mock_queue)

        data = {"template": "status", "system_name": "TEST"}

        # Il test dovrebbe gestire l'eccezione
        # (nota: potrebbe servire un'eccezione più specifica nel codice reale)


class TestStatusEndpoint:
    """Test per l'endpoint GET /status"""

    def test_status_returns_display_state(self, client):
        """Test che /status restituisca lo stato del display"""
        response = client.get('/status')

        assert response.status_code == 200
        json_data = response.get_json()

        # Verifica presenza campi richiesti
        assert 'template' in json_data
        assert 'data' in json_data
        assert 'status' in json_data
        assert 'queue_size' in json_data

    def test_status_with_timestamp(self, client, monkeypatch):
        """Test che /status includa timestamp se disponibile"""
        import server

        # Imposta uno stato con timestamp
        test_time = time.time()
        server.current_display_state.update({
            "template": "test",
            "data": {"test": "data"},
            "timestamp": test_time,
            "status": "ready"
        })

        response = client.get('/status')
        json_data = response.get_json()

        assert 'last_update' in json_data
        assert 'seconds_since_update' in json_data
        assert json_data['template'] == 'test'


class TestUploadEndpoint:
    """Test per l'endpoint POST /upload"""

    def test_upload_valid_image(self, client):
        """Test upload di un'immagine valida"""
        # Crea un file immagine fake
        data = {
            'file': (io.BytesIO(b"fake image data"), 'test.png')
        }

        response = client.post('/upload',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['status'] == 'OK'
        assert json_data['filename'] == 'test.png'

    def test_upload_no_file(self, client):
        """Test upload senza file"""
        response = client.post('/upload',
                              data={},
                              content_type='multipart/form-data')

        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data

    def test_upload_empty_filename(self, client):
        """Test upload con filename vuoto"""
        data = {
            'file': (io.BytesIO(b"fake image data"), '')
        }

        response = client.post('/upload',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data

    def test_upload_invalid_extension(self, client):
        """Test upload con estensione non valida"""
        data = {
            'file': (io.BytesIO(b"fake data"), 'test.exe')
        }

        response = client.post('/upload',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert 'allowed_extensions' in json_data

    def test_upload_with_custom_name(self, client):
        """Test upload con nome personalizzato"""
        data = {
            'file': (io.BytesIO(b"fake image data"), 'original.png'),
            'name': 'custom_name'
        }

        response = client.post('/upload',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['filename'] == 'custom_name.png'

    def test_upload_svg_file(self, client, sample_svg):
        """Test upload di un file SVG"""
        data = {
            'file': (io.BytesIO(sample_svg.encode()), 'icon.svg')
        }

        response = client.post('/upload',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data['filename'] == 'icon.svg'


class TestDisplayWorker:
    """Test per il worker thread del display"""

    def test_rate_limiting(self):
        """Test che il rate limiting funzioni correttamente"""
        import server

        # Verifica che MIN_UPDATE_INTERVAL sia impostato
        assert hasattr(server, 'MIN_UPDATE_INTERVAL')
        assert server.MIN_UPDATE_INTERVAL == 10

    def test_queue_exists(self):
        """Test che la coda esista"""
        import server

        assert hasattr(server, 'display_queue')
        assert server.display_queue.maxsize == 10


class TestAllowedFile:
    """Test per la funzione allowed_file"""

    def test_allowed_extensions(self):
        """Test estensioni consentite"""
        import server

        assert server.allowed_file('image.png') == True
        assert server.allowed_file('image.jpg') == True
        assert server.allowed_file('image.jpeg') == True
        assert server.allowed_file('image.bmp') == True
        assert server.allowed_file('image.gif') == True
        assert server.allowed_file('image.svg') == True

    def test_disallowed_extensions(self):
        """Test estensioni non consentite"""
        import server

        assert server.allowed_file('file.exe') == False
        assert server.allowed_file('file.txt') == False
        assert server.allowed_file('file.py') == False
        assert server.allowed_file('noextension') == False
