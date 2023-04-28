import json
import socket
import sys
import select
from socket import *
from log.server_log_config import server_log, log
from server_resource import ANSWER, ACTION

logger = server_log


@log()
def create_connect():
    """
        Command line options:
            -p <port> — TCP port for operation (uses 7777 by default);

            -a <addr> — the IP address to listen to (by default listens to all available addresses).
            """
    try:
        port = int(sys.argv[sys.argv.index('-p') + 1]) if '-p' in sys.argv else 7777
        if port < 1024 or port > 65536:
            raise ValueError
    except IndexError:
        logger.critical('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        logger.critical('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)
    try:
        addr = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else 'localhost'
    except IndexError:
        logger.critical('После параметра -\'a\' необходимо указать адрес в формате ххх.ххх.ххх.ххх')
        sys.exit(1)
    create_socket = socket(AF_INET, SOCK_STREAM)
    try:
        create_socket.bind((addr, port))
    except OSError:
        logger.critical("Проверьте правильность указанных адреса и порта")
        sys.exit(1)
    create_socket.listen(5)
    create_socket.settimeout(0.2)
    logger.debug('Socket сервера успешно создан')
    return create_socket


@log()
def send_server_message(client, code=200):
    message = json.dumps({"response": code, "alert": ANSWER[code]})
    logger.debug(f'Сформированно сообщение {ANSWER[code]}')
    client.send(message.encode('utf-8'))
    logger.debug(f'Сообщение {ANSWER[code]} отправлено клиенту {client.getpeername()}')


@log()
def send_message(w_list, message, all_clients):
    for client in w_list:
        try:
            for el in message:
                client.send(json.dumps(el).encode('utf-8'))
            send_server_message(client, 200)
        except:
            logger.debug(f'Клиент {client.fileno(), client.getpeername()} отключился от сервера')
            all_clients.remove(client)


@log()
def get_message(client):
    data = json.loads(client.recv(1000000).decode('utf-8'))
    logger.debug(f'Сообщение: \"{data["action"]}\" было отправлено клиентом: {client.getpeername()}')
    return data


@log()
def create_answer(request_dict):
    answer_list = []
    while request_dict:
        client, message = request_dict.popitem()
        if 'action' in message and message['action'] == 'msg' and 'time' in message and 'to' in message and \
                'from' in message and 'message' in message and 'encoding' in message:
            answer_list.append(message)
        elif 'action' in message and message['action'] in ACTION and 'time' in message and 'user' in message and \
                'type' in message:
            send_server_message(client, 200)
        else:
            send_server_message(client, 400)
    return answer_list


@log()
def read_reaquest(r_list, clients):
    list_message = {}
    for client in r_list:
        try:
            list_message[client] = get_message(client)
        except:
            logger.debug(f'Клиент {client.fileno(), client.getpeername()} отключился от сервера')
            clients.remove(client)
    return list_message


def main():
    my_socket = create_connect()
    list_clients = []
    answer_list = []
    while True:
        try:
            new_client, addr = my_socket.accept()
        except OSError as e:
            pass
        else:
            logger.debug(f'Получен запрос на соединение от клиента {str(addr)}')
            list_clients.append(new_client)
        finally:
            w_list = []
            r_list = []
            try:
                if list_clients:
                    r_list, w_list, e_list = select.select(list_clients, list_clients, [], 2)
            except Exception as e:
                pass
            if r_list:
                reaquest_list = read_reaquest(r_list, list_clients)
                if reaquest_list:
                    answer_list = [..., create_answer(reaquest_list)]
            if w_list and answer_list:
                send_message(w_list, answer_list, list_clients)

        # new_client.close()


if __name__ == "__main__":
    main()
