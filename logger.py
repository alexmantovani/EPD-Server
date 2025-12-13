import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Formatter con colori per output su console"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname_colored = f"{self.COLORS[record.levelname]}{record.levelname:8s}{self.RESET}"
        else:
            record.levelname_colored = f"{record.levelname:8s}"
        return super().format(record)


def setup_logger(
    name='epd-server',
    level=logging.INFO,
    log_to_file=True,
    log_to_console=True,
    log_dir='logs',
    max_bytes=10*1024*1024,  # 10MB
    backup_count=5,
    colored_console=True
):
    """
    Configura il sistema di logging centralizzato.

    Args:
        name: Nome del logger (default: 'epd-server')
        level: Livello di logging (default: logging.INFO)
        log_to_file: Se True, salva log su file (default: True)
        log_to_console: Se True, stampa log su console (default: True)
        log_dir: Directory per i log file (default: 'logs')
        max_bytes: Dimensione massima del log file prima della rotazione (default: 10MB)
        backup_count: Numero di backup file da mantenere (default: 5)
        colored_console: Se True, usa colori nella console (default: True)

    Returns:
        logging.Logger: Logger configurato
    """
    logger = logging.getLogger(name)

    # Rimuovi handler esistenti per evitare duplicati
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)

    # Formato dettagliato per file
    file_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Formato più semplice per console
    if colored_console:
        console_format = ColoredFormatter(
            fmt='%(asctime)s | %(levelname_colored)s | %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        console_format = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )

    # Handler per file con rotazione
    if log_to_file:
        # Crea directory logs se non esiste
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File principale
        log_file = os.path.join(log_dir, f'{name}.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        # File separato per errori
        error_log_file = os.path.join(log_dir, f'{name}-errors.log')
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)

    # Handler per console
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    return logger


def get_logger(name=None):
    """
    Ottieni un logger child del logger principale.

    Args:
        name: Nome del modulo (se None, usa 'epd-server')

    Returns:
        logging.Logger: Logger configurato
    """
    if name:
        return logging.getLogger(f'epd-server.{name}')
    return logging.getLogger('epd-server')


# Logger principale (da configurare all'avvio dell'applicazione)
main_logger = None


def init_logging(level=logging.INFO, debug_mode=False):
    """
    Inizializza il sistema di logging dell'applicazione.

    Args:
        level: Livello di logging (default: logging.INFO)
        debug_mode: Se True, abilita DEBUG level (default: False)

    Returns:
        logging.Logger: Logger principale
    """
    global main_logger

    if debug_mode:
        level = logging.DEBUG

    main_logger = setup_logger(
        name='epd-server',
        level=level,
        log_to_file=True,
        log_to_console=True,
        colored_console=True
    )

    main_logger.info("=" * 60)
    main_logger.info("EPD Server logging system initialized")
    main_logger.info(f"Log level: {logging.getLevelName(level)}")
    main_logger.info("=" * 60)

    return main_logger
