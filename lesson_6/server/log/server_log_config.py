import inspect
import logging
import os
from logging.handlers import TimedRotatingFileHandler

server_log = logging.getLogger('server_app.' + __name__)
default_formatter = logging.Formatter("%(asctime)s %(levelname)s %(module)s %(message)s")
sl = TimedRotatingFileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.log'),
                              encoding='utf-8', interval=1,
                              when='d', backupCount=1, delay=True, utc=False)
sl.setFormatter(default_formatter)
sl.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(default_formatter)
server_log.addHandler(sl)
server_log.addHandler(console)
server_log.setLevel(logging.DEBUG)


class log:
    def __call__(self, func):
        def loger(*args, **kwargs):
            result = func(*args, **kwargs)
            server_log.debug(f'Вызвана функция {func.__name__} с аргументами {args, kwargs}'
                             f' из функции {inspect.stack()[1][3]}')
            return result

        return loger


if __name__ == '__main__':
    server_log.info('Тестовый запуск логирования')
