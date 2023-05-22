import json
import random
import sys
import threading
import time
from socket import *
from log.client_log_config import client_log, log
from client_resource import ClientVerifier, ENCODING_MSG

logger = client_log
username = f'Guest-{random.randint(0, 1000)}'


@log
def send_presence_message(client_socket):
    send_message(client_socket, {"action": 'presence',
                                 "time": time.time(),
                                 "type": "status",
                                 "user": {"account_name": username,
                                          "status": "Yep, I am here!"}
                                 })


@log
def send_authenticate_message(client_socket):
    send_message(client_socket, {"action": "authenticate",
                                 "time": time.time(),
                                 "user": {"account_name": username,
                                          "password": "CorrectPassword"}
                                 })


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


class ClientTransmiter(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, user_name, socket):
        self.user_name = user_name
        self.socket = socket
        super().__init__()

    def create_exit_message(self):
        return {"action": "quit",
                "time": time.time(),
                "user": {"account_name": self.user_name}
                }

    def send_client_message(self)   :
        to_user = input('Введите имя получателя сообщения: ')
        text_message = input('Введите текст сообщения: ')
        client_message = {
            "action": "msg",
            "time": time.time(),
            "to": to_user,
            "from": self.user_name,
            "encoding": ENCODING_MSG,
            "message": text_message
        }
        send_message(self.socket, client_message)
        g_message = get_message(self.socket)["response"]
        while not g_message == 200:
            send_message(self.socket, client_message)
            g_message = get_message(self.socket)["response"]

    def run(self):
        while True:
            print('Выберите действие: \'message\' - отправить сообщение; \'exit\' - выход')
            user_command = input('Ваша комманда: ')
            if user_command == 'exit':
                send_message(self.socket, self.create_exit_message())
                print('Завершение работы.')
                time.sleep(0.5)
                break
            elif user_command == 'message':
                # pass
                self.send_client_message()


class ClientReceiver(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, user_name, socket):
        self.user_name = user_name
        self.socket = socket
        super().__init__()

    def run(self):
        while True:
            try:
                g_message = get_message(self.socket)
                if 'action' in g_message and g_message[
                    'action'] == 'msg' and 'time' in g_message and 'to' in g_message and \
                        'from' in g_message and 'message' in g_message and 'encoding' in g_message:
                    from_user = g_message["from"]
                    text_message = g_message["message"]
                    logger.info(f'От пользователя "{from_user}" получено сообщение "{text_message}"')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break


@log
def create_connect():
    """
Script command line parameters client.py <addr> <port> <username>:
    addr — server ip address;

    port — tcp port on the server, by default 7777;

    username — name of user, by default Guest-XXX.
    """
    global username
    try:
        addr = sys.argv[1]
        port = int(sys.argv[2])
        if port < 1024 or port > 65536:
            raise ValueError
    except IndexError:
        addr = 'localhost'
        port = 7777
    except ValueError:
        logger.critical('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)
    try:
        username = sys.argv[3]
    except IndexError:
        logger.debug(f'Вы неуказали имя пользователя при запуске. Для работы выбрано имя пользователя  {username}')
    logger.debug(f'Клиент запущен от пользователя {username}')
    create_socket = socket(AF_INET, SOCK_STREAM)
    try:
        create_socket.connect((addr, port))
    except OSError:
        logger.critical("Проверьте правильность указанных адреса и порта")
        sys.exit(1)
    send_presence_message(create_socket)
    g_message = get_message(create_socket)["response"]
    while g_message == 409:
        old_username = username
        username = f'Guest-{random.randint(0, 1000)}'
        logger.debug(
            f"Пользователь с именем '{old_username}' уже уже подключился к серверу. Ваше имя изменено на '{username}'")
        send_presence_message(create_socket)
        g_message = get_message(create_socket)["response"]
    if g_message == 200:
        return create_socket


def main():
    my_socket = create_connect()
    print(my_socket, username)

    receiver = ClientReceiver(username, my_socket)
    receiver.daemon = True
    receiver.start()

    my_interface = ClientTransmiter(username, my_socket)
    my_interface.daemon = True
    my_interface.start()
    logger.debug('Запущены процессы')

    while True:
        time.sleep(1)
        if receiver.is_alive() and my_interface.is_alive():
            continue
        break


if __name__ == "__main__":
    main()
