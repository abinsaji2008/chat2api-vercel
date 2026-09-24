import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
class Logger:
    @staticmethod
    def info(message): logging.info(str(message))
    @staticmethod
    def warning(message): logging.warning(str(message))
    @staticmethod
    def error(message): logging.error(str(message))
    @staticmethod
    def debug(message): logging.debug(str(message))
logger=Logger()
