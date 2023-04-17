import json
import socket
import sys
from socket import *

from server_resource import ANSWER


def create_server_message(code=200):
    return json.dumps({
        "response": code,
        "alert": ANSWER[code]
    })


def create_connect():
    """
    Command line options:
        -p <port> — TCP port for operation (uses 7777 by default);

        -a <addr> — the IP address to listen to (by default listens to all available addresses).
        """
    try:
        if '-p' in sys.argv:
            port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            port = 7777
        if port < 1024 or port > 65536:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print(
            'В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)
    try:
        if '-a' in sys.argv:
            addr = sys.argv[sys.argv.index('-a') + 1]
        else:
            addr = 'localhost'
    except IndexError:
        print('После параметра -\'a\' необходимо указать адрес в формате ххх.ххх.ххх.ххх')
        sys.exit(1)
    create_socket = socket(AF_INET, SOCK_STREAM)
    try:
        create_socket.bind((addr, port))
    except OSError:
        print("Проверьте правильность указанных адреса и порта")
        sys.exit(1)
    create_socket.listen(5)
    return create_socket


def send_message(client, code=200):
    client.send(create_server_message(code).encode('utf-8'))


def get_message(server_socket):
    client, addr = server_socket.accept()
    data = json.loads(client.recv(1000000).decode('utf-8'))
    print('Сообщение: ', data, ', было отправлено клиентом: ', addr)
    return client


def main():
    my_socket = create_connect()
    while True:
        new_client = get_message(my_socket)
        send_message(new_client, 200)
        new_client.close()


if __name__ == "__main__":
    main()
