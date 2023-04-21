import logging
import os
from logging.handlers import RotatingFileHandler

client_log = logging.getLogger('client_app.' + __name__)
default_formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s")
cl = RotatingFileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client.log'),
                         mode='a', maxBytes=200000,
                         encoding='utf-8', backupCount=3, delay=True)
cl.setFormatter(default_formatter)
cl.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(default_formatter)
client_log.addHandler(cl)
client_log.addHandler(console)
client_log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    client_log.info('Тестовый запуск логирования')
