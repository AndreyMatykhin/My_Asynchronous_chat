import json
import socket
import sys
import select
from socket import *

from server_storage import Storage
from log.server_log_config import server_log, log
from server_resource import ANSWER, ACTION, ServerVerifier, ServerPort

logger = server_log


class WorkingServer(metaclass=ServerVerifier):
    port = ServerPort()

    def __init__(self, database):
        try:
            port = int(sys.argv[sys.argv.index('-p') + 1]) if '-p' in sys.argv else 7777
        except IndexError:
            logger.critical('После параметра -\'p\' необходимо указать номер порта.')
            sys.exit(1)
        else:
            self.port = port
        try:
            addr = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else 'localhost'
        except IndexError:
            logger.critical('После параметра -\'a\' необходимо указать адрес в формате ххх.ххх.ххх.ххх')
            sys.exit(1)
        else:
            self.addr = addr
        create_socket = socket(AF_INET, SOCK_STREAM)
        try:
            create_socket.bind((self.addr, self.port))
        except OSError:
            logger.critical("Проверьте правильность указанных адреса и порта")
            sys.exit(1)
        create_socket.settimeout(0.2)
        self.socket = create_socket
        self.socket.listen()
        logger.debug('Socket сервера успешно создан')
        self.users = {}
        self.list_clients = []
        self.answer_list = []
        self.database = database

    def loop(self):
        while True:
            try:
                new_client, addr = self.socket.accept()
            except OSError as e:
                pass
            else:
                fg_message = get_message(new_client)
                if 'action' in fg_message and fg_message['action'] == 'presence' and 'time' in fg_message and \
                        'user' in fg_message and 'account_name' in fg_message['user'] and 'status' in fg_message[
                    'user']:
                    logger.debug(f'Получен запрос на соединение от клиента {fg_message["user"]["account_name"]}')
                    if fg_message['user']['status'] == "Yep, I am here!" and not (
                            fg_message['user']['account_name'] in self.users):
                        self.users[fg_message['user']['account_name']] = new_client
                        self.list_clients.append(new_client)
                        logger.debug(f'Присоединился клиент {fg_message["user"]["account_name"]}')
                        send_server_message(new_client, 200)
                    else:
                        logger.debug(f'Клиент {fg_message["user"]["account_name"]} уже подключен')
                        send_message(new_client, 409)
                else:
                    logger.debug(f'Получено неверное сообщение')
                    send_server_message(new_client, 400)
            w_list = []
            r_list = []
            try:
                if self.list_clients:
                    r_list, w_list, e_list = select.select(self.list_clients, self.list_clients, [], 2)
            except Exception as e:
                pass
            if r_list:
                reaquest_list = read_reaquest(r_list, self.list_clients)
                if reaquest_list:
                    self.answer_list = create_answer(reaquest_list, self.list_clients, self.users)
            if self.answer_list:
                send_message(self.users, self.answer_list, w_list)


@log()
def send_server_message(client, code=200):
    message = json.dumps({"response": code, "alert": ANSWER[code]})
    logger.debug(f'Сформированно сообщение {ANSWER[code]}')
    client.send(message.encode('utf-8'))
    logger.debug(f'Сообщение {ANSWER[code]} отправлено клиенту {client.getpeername()}')


@log()
def send_message(users, message, w_list):
    print(message)
    while message:
        mess = message.pop()
        if mess['to'] in users and users[mess['to']] in w_list:
            users[mess['to']].send(json.dumps(mess).encode('utf-8'))
        else:
            logger.debug(f"Пользователя с именем {mess['to']} нет среди клиентов сервера")


@log()
def get_message(client):
    data = json.loads(client.recv(1000000).decode('utf-8'))
    logger.debug(f'Сообщение: \"{data["action"]}\" было отправлено клиентом: {client.getpeername()}')
    return data


@log()
def create_answer(request_dict, clients, users):
    answer_list = []
    while request_dict:
        client, message = request_dict.popitem()
        if 'action' in message and message['action'] == 'msg' and 'time' in message and 'to' in message and \
                'from' in message and 'message' in message and 'encoding' in message:
            answer_list.append(message)
            send_server_message(client, 200)
        elif 'action' in message and message['action'] == 'quit' and 'time' in message and 'user' in message and \
                'account_name' in message['user']:
            send_server_message(client, 200)
            del users[message['user']['account_name']]
            client.close()
            clients.remove(client)
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
    database = Storage()
    server = WorkingServer(database)
    server.loop()


if __name__ == "__main__":
    main()
