import dis
import json
import sys
import threading
import time
import socket

from PyQt5.QtCore import QObject, pyqtSignal

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
socket_lock = threading.Lock()


class ClientSocket(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, ip_address, port, database, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.database = database
        self.username = username
        self.my_socket = None
        self.create_connection(ip_address, port)
        try:
            self.update_list_users_database()
        except OSError as err:
            if err.errno:
                logger.critical(f'Потеряно соединение с сервером.')
            logger.error('Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            logger.critical(f'Потеряно соединение с сервером.')
        self.running = True

    def create_connection(self, addr, port):
        """
        # Script command line parameters client.py <addr> <port> <username>:
        #     addr — server ip address;
        #
        #     port — tcp port on the server, by default 7777;
        #
        #     username — name of user, by default Guest-XXX.
        #     """
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.settimeout(5)
        status_connected = False
        for i in range(5):
            try:
                self.my_socket.connect((addr, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                status_connected = True
                break
            time.sleep(1)
        if status_connected:
            try:
                with socket_lock:
                    self.send_presence_message()
                    g_message = get_message(self.my_socket)["response"]
                    if g_message == 409:
                        logger.info(f"Пользователь с именем '{self.username}' уже уже подключился к серверу.")
                        sys.exit(1)
                    elif g_message == 200:
                        logger.info(f'Клиент запущен от пользователя {self.username}')
            except (OSError, json.JSONDecodeError):
                logger.critical('Потеряно соединение с сервером!')
            logger.info('Соединение с сервером успешно установлено.')
        else:
            logger.critical('Не удалось установить соединение с сервером')
            sys.exit(1)

    def run(self):
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.my_socket.settimeout(0.5)
                    g_message = get_message(self.my_socket)
                except OSError as err:
                    if err.errno:
                        logger.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError):
                    logger.critical(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    self.database.save_message(g_message)
                finally:
                    self.my_socket.settimeout(5)

    @log
    def send_presence_message(self):
        send_message(self.my_socket, {"action": 'presence',
                                      "time": time.time(),
                                      "type": "status",
                                      "user": {"account_name": self.username,
                                               "status": "Yep, I am here!"}
                                      })

    @log
    def send_get_all_users(self):
        """
        Script for requesting a list of names of all users
        :param socket: socket
        :param username: str
        """
        message = {"action": 'all_users',
                   "time": time.time(),
                   "user": {"account_name": self.username,
                            }
                   }
        with socket_lock:
            send_message(self.my_socket, message)
            logger.info('Отправлен запрос на получения списка всех пользователей')
            g_message = get_message(self.my_socket)
            if g_message['response'] == 202:
                return g_message['alert']
            else:
                return None

    @log
    def send_get_contacts(self):
        """
        Script for requesting a list of names of all contacts of user
        :param client_socket: socket
        :param username: str
        """
        message = {"action": 'get_contacts',
                   "time": time.time(),
                   "user": {"account_name": self.username,
                            }
                   }
        with socket_lock:
            send_message(self.my_socket, message)
            logger.info('Отправлен запрос на получения списка контактов')
            g_message = get_message(self.my_socket)
            if g_message['response'] == 202:
                return g_message['alert']
            else:
                return None

    def send_client_message(self, to_user, text_message):
        client_message = {
            "action": "msg",
            "time": time.time(),
            "to": to_user,
            "from": self.username,
            "encoding": ENCODING_MSG,
            "message": text_message
        }
        with socket_lock:
            send_message(self.my_socket, client_message)
            self.database.save_message(client_message)
            return True if get_message(self.my_socket)['response'] == 200 else False

    def update_list_users_database(self):
        all_users = self.send_get_all_users()
        list_contacts = self.send_get_contacts()
        self.database.add_all_users(all_users, list_contacts)
        logger.info(f'Список пользователей мессенджера в базе обновлен')

    @log
    def process_server_answer(self, g_message):
        # if g_message == 409:
        self.database.save_message(g_message)

    @log
    def shutdown(self):
        self.running = False
        message = {"action": "quit",
                   "time": time.time(),
                   "user": {"account_name": self.username}
                   }
        with socket_lock:
            try:
                send_message(self.my_socket, message)
            except OSError:
                pass
        logger.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    @log
    def send_add_contact(self, nickname):
        message = {"action": 'add_contact',
                   "user_id": nickname,
                   "time": time.time(),
                   "user_login": self.username
                   }
        with socket_lock:
            send_message(self.my_socket, message)
            logger.info(
                f'Отправлен запрос на добавление контакта {nickname} в список контактов пользователя {self.username}')
            return True if get_message(self.my_socket)['response'] == 200 else False

    @log
    def send_del_contact(self, nickname):
        message = {"action": 'del_contact',
                   "user_id": nickname,
                   "time": time.time(),
                   "user_login": self.username
                   }
        with socket_lock:
            send_message(self.my_socket, message)
            logger.info(f'Отправлен запрос на удаление контакта {nickname} из список контактов пользователя {self.username}')
            return True if get_message(self.my_socket)['response'] == 200 else False


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


# @log
# def send_authenticate_message(client_socket, username):
#     send_message(client_socket, {"action": "authenticate",
#                                  "time": time.time(),
#                                  "user": {"account_name": username,
#                                           "password": "CorrectPassword"}
#                                  })


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
