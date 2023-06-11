import dis
import json
import socket

from log.server_log_config import server_log, log

ANSWER = {
    # 1xx — информационные сообщения:
    100: 'базовое уведомление',
    101: 'важное уведомление',
    # 2xx — успешное завершение:
    200: 'OK',
    201: '(created) — объект создан',
    202: '(accepted) — подтверждение',
    # 4xx — ошибка на стороне клиента:
    400: 'неправильный запрос/JSON-объект',
    401: 'не авторизован',
    402: 'неправильный логин/пароль',
    403: '(forbidden) — пользователь заблокирован',
    404: '(not found) — пользователь/чат отсутствует на сервере',
    409: '(conflict) — уже имеется подключение с указанным логином',
    410: '(gone) — адресат существует, но недоступен (offline)',
    # 5xx — ошибка на стороне сервера:
    500: 'ошибка сервера.'
}
ACTION = [
    "presence",  # — присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online;
    "prоbe",  # — проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online;
    "msg",  # — простое сообщение пользователю или в чат;
    "quit",  # — отключение от сервера;
    "authenticate",  # — авторизация на сервере;
    "join",  # — присоединиться к чату;
    "leave"  # — покинуть чат.
]


@log()
def create_server_message(code: int, alert=''):
    message = {"response": code, "alert": alert} if alert else {"response": code, "alert": ANSWER[code]}
    server_log.info(f'Сформированно сообщение "{message}"')
    return message


@log()
def send_message(client_socket, transmit_message):
    client_socket.send(json.dumps(transmit_message).encode('utf-8'))
    server_log.info(f'Сообщение отправлено клиенту {client_socket.getpeername()}')
    return f'Отправлено сообщение: {transmit_message}'


@log()
def get_message(client):
    data = json.loads(client.recv(1000000).decode('utf-8'))
    server_log.info(f'Сообщение: \"{data["action"] if "action" in data else None}\" было отправлено клиентом: {client.getpeername()}')
    print(data)
    return data


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        attrs = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in methods and 'AF_INET' in methods):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(clsname, bases, clsdict)


logger = server_log


class ServerPort:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {value}. В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

def login_required(func):
    def checker(*args, **kwargs):
        # проверяем, что первый аргумент - экземпляр MessageProcessor
        # Импортить необходимо тут, иначе ошибка рекурсивного импорта.
        from server import WorkingServer
        if isinstance(args[0], WorkingServer):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == 'presence':
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker