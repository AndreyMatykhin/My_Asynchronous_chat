import dis
import json
import threading
import time

from log.client_log_config import client_log, log

logger = client_log
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
ENCODING_MSG = 'ascii'


@log
def send_message(client_socket, transmit_message):
    client_socket.send(json.dumps(transmit_message).encode('utf-8'))
    logger.info(f'Сообщение отправлено на сервер {client_socket.getpeername()}')
    return f'Отправлено сообщение: {transmit_message}'


@log
def get_message(client_socket, max_length=1024):
    answer = json.loads(client_socket.recv(max_length).decode("utf-8"))
    logger.info(f'Получен сообщение {answer} от сервера {client_socket.getpeername()}')
    return answer


@log
def send_presence_message(client_socket, username):
    send_message(client_socket, {"action": 'presence',
                                 "time": time.time(),
                                 "type": "status",
                                 "user": {"account_name": username,
                                          "status": "Yep, I am here!"}
                                 })


@log
def send_get_contacts(socket, username):
    """
    Script for requesting a list of names of all contacts of user
    :param client_socket: socket
    :param username: str
    """
    message = {"action": 'get_contacts',
               "time": time.time(),
               "user": {"account_name": username,
                        }
               }
    send_message(socket, message)
    client_log.info('Отправлен запрос на получения списка контактов')
    g_message = get_message(socket)
    if g_message['response'] == 202:
        return g_message['alert']
    else:
        return None


@log
def send_get_all_users(socket, username):
    """
    Script for requesting a list of names of all users
    :param socket: socket
    :param username: str
    """
    message = {"action": 'all_users',
               "time": time.time(),
               "user": {"account_name": username,
                        }
               }
    send_message(socket, message)
    client_log.info('Отправлен запрос на получения списка всех пользователей')
    g_message = get_message(socket)
    if g_message['response'] == 202:
        return g_message['alert']
    else:
        return None


@log
def send_add_contact(socket, username, nickname):
    """
    Script for requesting a list of names of all users
    :param socket: socket
    :param username: str
    """
    message = {"action": 'add_contact',
               "user_id": nickname,
               "time": time.time(),
               "user_login": username
               }
    send_message(socket, message)
    client_log.info(f'Отправлен запрос на добавление контакта {nickname} в список контактов пользователя {username}')
    g_message = get_message(socket)
    if g_message['response'] == 200:
        return g_message['alert']
    else:
        return None


@log
def send_del_contact(socket, username, nickname):
    """
    Script for requesting a list of names of all users
    :param socket: socket
    :param username: str
    """
    message = {"action": 'del_contact',
               "user_id": nickname,
               "time": time.time(),
               "user_login": username
               }
    send_message(socket, message)
    client_log.info(f'Отправлен запрос на удаление контакта {nickname} из список контактов пользователя {username}')
    g_message = get_message(socket)
    if g_message['response'] == 200:
        return g_message['alert']
    else:
        return None


@log
def send_authenticate_message(client_socket, username):
    send_message(client_socket, {"action": "authenticate",
                                 "time": time.time(),
                                 "user": {"account_name": username,
                                          "password": "CorrectPassword"}
                                 })


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
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
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(clsname, bases, clsdict)
