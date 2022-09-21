import logging
import sys

from const import LOG_FILE


def logging_config():
    file_handler = logging.FileHandler(filename=LOG_FILE)
    stdout_handler = logging.StreamHandler(sys.stdout)
    logging.basicConfig(handlers=[file_handler, stdout_handler],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        level=logging.DEBUG)
