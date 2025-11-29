# Test EPD Server

Questa guida spiega come eseguire i test per il server EPD.

## Installazione dipendenze di test

Prima di eseguire i test, installa le dipendenze necessarie:

```bash
pip install -r requirements-dev.txt
```

## Struttura dei test

I test sono organizzati nella cartella `tests/` con tre file principali:

- **tests/test_server.py**: Test per gli endpoint HTTP del server Flask
  - `POST /update` - Aggiornamento display
  - `GET /status` - Stato corrente del display
  - `POST /upload` - Upload immagini

- **tests/test_utils.py**: Test per le funzioni di utilità
  - `bbox()` - Calcolo dimensioni testo
  - `get_ip()` - Rilevamento indirizzo IP
  - `svg_to_image()` - Conversione SVG in immagine
  - `load_icon()` - Caricamento icone (BMP, PNG, SVG)

- **tests/test_templates.py**: Test per i template di rendering
  - `template_status` - Template status
  - `template_warning` - Template warning
  - `template_alert` - Template alert
  - `template_success` - Template success
  - `template_info` - Template info

- **tests/conftest.py**: Configurazione pytest e fixture comuni

## Esecuzione dei test

### Eseguire tutti i test

```bash
pytest
```

### Eseguire test specifici

```bash
# Test solo del server
pytest tests/test_server.py

# Test solo delle utility
pytest tests/test_utils.py

# Test solo dei template
pytest tests/test_templates.py

# Test di una classe specifica
pytest tests/test_server.py::TestUpdateEndpoint

# Test di un singolo test
pytest tests/test_server.py::TestUpdateEndpoint::test_update_with_valid_template
```

### Eseguire test con output verboso

```bash
pytest -v
```

### Eseguire test con coverage

```bash
pytest --cov=. --cov-report=html
```

Questo genera un report di copertura nella cartella `htmlcov/`.

### Eseguire test con output dettagliato

```bash
pytest -vv -s
```

L'opzione `-s` mostra i print statements durante i test.

## Fixtures disponibili

I test utilizzano diverse fixture definite in `tests/conftest.py`:

- **mock_epd**: Mock del display EPD hardware
- **app**: Applicazione Flask configurata per i test
- **client**: Client di test Flask per fare richieste HTTP
- **epd_colors**: Dizionario dei colori EPD
- **sample_svg**: SVG di esempio per i test

## Esempio di output

```
============================= test session starts ==============================
platform darwin -- Python 3.x.x, pytest-7.4.3
collected 45 items

test_server.py .............                                             [ 28%]
test_utils.py ..............                                             [ 60%]
test_templates.py ..................                                     [100%]

============================== 45 passed in 2.34s ===============================
```

## Coverage Report

Per vedere la copertura del codice:

```bash
pytest --cov=. --cov-report=term-missing
```

Output esempio:
```
---------- coverage: platform darwin, python 3.x.x -----------
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
server.py              150     10    93%   45-48, 120-125
utils.py                45      2    96%   67-68
templates/status.py     35      0   100%
templates/warning.py    32      0   100%
templates/alert.py      38      0   100%
templates/success.py    25      0   100%
templates/info.py       30      0   100%
--------------------------------------------------
TOTAL                  355     12    97%
```

## Note importanti

1. **Hardware Mock**: I test mockano l'hardware EPD, quindi possono essere eseguiti senza device fisico collegato.

2. **Isolamento**: Ogni test è isolato e non modifica lo stato globale permanentemente.

3. **File temporanei**: I test che richiedono file usano `tmp_path` di pytest per creare file temporanei che vengono automaticamente puliti.

4. **Threading**: Il worker thread del display non viene avviato durante i test per evitare race conditions.

## Troubleshooting

### Import errors

Se ricevi errori di import, assicurati di essere nella directory del progetto:

```bash
cd /Users/AlexBook/PycharmProjects/EPD-Server
pytest
```

### Dipendenze mancanti

Se ricevi errori sulle dipendenze:

```bash
pip install -r requirements-dev.txt
```

### Test falliti

Per vedere più dettagli sui test falliti:

```bash
pytest -vv --tb=long
```

## Continuous Integration

I test possono essere integrati in pipeline CI/CD (GitHub Actions, GitLab CI, ecc.) aggiungendo:

```yaml
# Esempio .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=. --cov-report=xml
```
