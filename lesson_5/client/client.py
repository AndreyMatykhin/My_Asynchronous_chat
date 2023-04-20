import json
import sys
import time
from socket import *
from log.client_log_config import client_log
from client_resource import ACTION

logger = client_log


def create_client_message(action='presence', message={"type": "status", "user": {"account_name": "C0deMaver1ck",
                                                                                 "status": "Yep, I am here!"}}):
    if action in ACTION:
        client_message = {
            "action": action,
            "time": time.time()
        }
        if isinstance(message, dict):
            client_message.update(message)
            logger.debug(f'Сформированно ссобщение {client_message}')
            return json.dumps(client_message)
        else:
            logger.error('Неправильный формат сообщения')
            raise ValueError
    else:
        logger.error(f'Недопустимое действие {action}')
        raise ValueError


def send_message(client_socket, transmit_message):
    client_socket.send(transmit_message.encode('utf-8'))
    logger.debug(f'Сообщение отправлено на сервер {client_socket.getpeername()}')
    return f'Отправлено сообщение: {create_client_message()}'


def get_message(client_socket, max_length=1024):
    answer= json.loads(client_socket.recv(max_length).decode("utf-8"))
    logger.debug(f'Получен ответ {answer["alert"]} от сервера {client_socket.getpeername()}')
    return f'Получен ответ {answer}'


def create_connect():
    """
Script command line parameters client.py <addr> [<port>]:
    addr — server ip address;

    port — tcp port on the server, by default 7777.
    """
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
    create_socket = socket(AF_INET, SOCK_STREAM)
    try:
        create_socket.connect((addr, port))
    except OSError:
        logger.critical("Проверьте правильность указанных адреса и порта")
        sys.exit(1)
    return create_socket


def main():
    my_socket = create_connect()
    send_message(my_socket, create_client_message())
    get_message(my_socket)
    my_socket.close()


if __name__ == "__main__":
    main()
