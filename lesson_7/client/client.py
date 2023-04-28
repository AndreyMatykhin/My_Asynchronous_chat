import json
import sys
import time
from socket import *
from log.client_log_config import client_log, log
from client_resource import ACTION

logger = client_log


@log
def create_client_message(action='presence', message={"type": "status", "user": {"account_name": "C0deMaver1ck",
                                                                                 "status": "Yep, I am here!"}}):
    if action in ACTION:
        client_message = {
            "action": action,
            "time": time.time()
        }
        if isinstance(message, dict):
            client_message.update(message)
            logger.debug(f'Сформированно собщение {client_message}')
            return client_message
        else:
            logger.error('Неправильный формат сообщения')
            raise ValueError
    else:
        logger.error(f'Недопустимое действие {action}')
        raise ValueError


@log
def send_message(client_socket, transmit_message):
    client_socket.send(json.dumps(transmit_message).encode('utf-8'))
    logger.debug(f'Сообщение отправлено на сервер {client_socket.getpeername()}')
    return f'Отправлено сообщение: {transmit_message}'


@log
def get_message(client_socket, max_length=1024):
    answer = json.loads(client_socket.recv(max_length).decode("utf-8"))
    logger.debug(f'Получен сообщение {answer} от сервера {client_socket.getpeername()}')
    return answer


@log
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
    try:
        mode = sys.argv[3]
    except IndexError:
        logger.debug('Для клиента установлен по умоляанию режим ожидания сообщений от сервера')
        mode = 'r'
    create_socket = socket(AF_INET, SOCK_STREAM)
    try:
        create_socket.connect((addr, port))
    except OSError:
        logger.critical("Проверьте правильность указанных адреса и порта")
        sys.exit(1)
    return create_socket, mode


def main():
    my_socket, mode = create_connect()
    if mode == 'r':
        while True:
            g_message = get_message(my_socket)
            if 'response' in g_message and g_message['response'] == 200:
                logger.debug('Все сообщения от сервера получены, клиент закрыт')
                break
                # my_socket.close()
                # sys.exit(1)

    elif mode == 'w':
        # send_message(my_socket, create_client_message())
        send_message(my_socket, create_client_message(action='msg', message={"to": "all",
                                                                             "from": "C0deMaver1ck",
                                                                             "encoding": "utf-8",
                                                                             "message": "Yep, I am here!"}))
    my_socket.close()
    sys.exit(1)


if __name__ == "__main__":
    main()
