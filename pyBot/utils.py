import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

import common


class BetterRotatingFileHandler(RotatingFileHandler):

    def _open(self):
        Path(os.path.dirname(self.baseFilename)).mkdir(parents = True, exist_ok = True)
        return logging.handlers.RotatingFileHandler._open(self)


def setup_logging():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root = logging.root
    root.setLevel(logging.DEBUG)

    info_handler = BetterRotatingFileHandler(filename = 'logs/log', maxBytes = 10 * (1 << 20), backupCount = 10, encoding = 'utf-8')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    root.addHandler(info_handler)

    error_handler = BetterRotatingFileHandler(filename = 'logs/error', maxBytes = 10 * (1 << 20), backupCount = 10, encoding = 'utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root.addHandler(error_handler)

    all_debug_handler = BetterRotatingFileHandler(filename = 'logs/all_debug', maxBytes = 10 * (1 << 20), backupCount = 10, encoding = 'utf-8')
    all_debug_handler.setLevel(logging.DEBUG)
    all_debug_handler.setFormatter(formatter)
    root.addHandler(all_debug_handler)

    logger = logging.getLogger(common.LOGGER_NAME)
    debug_handler = BetterRotatingFileHandler(filename = 'logs/debug', maxBytes = 10 * (1 << 20), backupCount = 10, encoding = 'utf-8')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)
