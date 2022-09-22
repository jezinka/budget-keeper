import logging
import sys
from logging.handlers import RotatingFileHandler

from const import LOG_FILE


def logging_config():
    file_handler = RotatingFileHandler(filename=LOG_FILE, maxBytes=1000000, backupCount=5)
    stdout_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(handlers=[file_handler, stdout_handler],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.DEBUG)
