import logging
import sys


def logging_config():
    file_handler = logging.FileHandler(filename='logs/bk.log')
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(handlers=handlers, datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
