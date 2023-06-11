import binascii
import hmac
import os
import socket
import sys
import select
import threading
import time
from socket import *

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from server_gui import MainWindow, gui_create_model, HistoryWindow, ConfigWindow, RegisterWindow, RemoveWindow
from server_storage import Storage
from log.server_log_config import server_log, log
from server_resource import ServerVerifier, ServerPort, create_server_message, send_message, get_message

change_count_connection = True


class WorkingServer(threading.Thread, metaclass=ServerVerifier):
    port = ServerPort()

    def __init__(self):
        try:
            port = int(sys.argv[sys.argv.index('-p') + 1]) if '-p' in sys.argv else 7777
        except IndexError:
            server_log.critical('После параметра -\'p\' необходимо указать номер порта.')
            sys.exit(1)
        else:
            self.port = port
        try:
            addr = sys.argv[sys.argv.index('-a') + 1] if '-a' in sys.argv else 'localhost'
        except IndexError:
            server_log.critical('После параметра -\'a\' необходимо указать адрес в формате ххх.ххх.ххх.ххх')
            sys.exit(1)
        else:
            self.addr = addr
        create_socket = socket(AF_INET, SOCK_STREAM)
        try:
            create_socket.bind((self.addr, self.port))
        except OSError:
            server_log.critical("Проверьте правильность указанных адреса и порта")
            sys.exit(1)
        create_socket.settimeout(0.2)
        self.socket = create_socket
        self.socket.listen()
        server_log.info('Socket сервера успешно создан')
        self.users_dict = {}  # словарь подключенных клиентов
        self.list_active_clients = []  # список всех сокетов клиентов
        self.request_dict = {}  # словарь входящих сообщений
        self.answer_dict = {}  # словарь исходящих сообщений
        self.database = Storage()  # база данных
        self.w_list = []  # список входящих сокетов клиентов
        self.r_list = []  # список исходящих сокетов клиентов
        super().__init__()

    def run(self):
        while True:
            try:
                new_client, addr = self.socket.accept()
            except OSError as e:
                pass
            else:
                server_log.info(f'Установлено соедение с ПК {addr}')
                self.list_active_clients.append(new_client)
            try:
                if self.list_active_clients:
                    self.r_list, self.w_list, e_list = select.select(self.list_active_clients, self.list_active_clients,
                                                                     [], 0)
            except OSError as err:
                server_log.error(f'Ошибка работы с сокетами: {err}')
            if self.r_list:
                self.read_reaquest()
                if self.request_dict:
                    self.create_answer()
            if self.answer_dict:
                self.send_answer()

    @log()
    def read_reaquest(self):
        global change_count_connection
        for client in self.r_list:
            try:
                self.request_dict[client] = get_message(client)
            except:
                server_log.info(f'Клиент {client.fileno(), client.getpeername()} отключился от сервера')
                for user in self.users_dict:
                    if self.users_dict[user] == client:
                        del self.users_dict[user]
                        break
                self.list_active_clients.remove(client)
                if client in self.r_list:
                    self.r_list.remove(client)
                change_count_connection = True

    @log()
    def create_answer(self):
        global change_count_connection
        while self.request_dict:
            client, message = self.request_dict.popitem()
            # Обработка запроса-представления
            if 'action' in message and message['action'] == 'presence' and 'time' in message and \
                    'user' in message and 'account_name' in message['user'] and 'status' in message['user'] and \
                    message['user']['status'] == "Yep, I am here!" and 'pubkey' in message['user']:
                if message['user']['account_name'] in self.users_dict:
                    server_log.info(f'Клиент {message["user"]["account_name"]} уже подключен')
                    self.answer_dict[client] = create_server_message(409)
                elif self.database.check_user(message['user']['account_name']):
                    server_log.info(f'Получен запрос на соединение от клиента {message["user"]["account_name"]}')
                    random_str = binascii.hexlify(os.urandom(64))
                    hash = hmac.new(self.database.get_hash_passwd(message["user"]["account_name"]), random_str, 'MD5')
                    digest = hash.digest()
                    try:
                        send_message(client,
                                     create_server_message(511, random_str.decode('ascii')))
                        g_message = get_message(client)
                    except OSError as err:
                        server_log.debug('Error in auth, data:', exc_info=err)
                        client.close()
                        return
                    client_digest = binascii.a2b_base64(g_message['alert'])
                    print(digest, client_digest, hmac.compare_digest(digest, client_digest))
                    if 'code' in g_message and g_message['code'] == 511 and hmac.compare_digest(
                            digest, client_digest):
                        self.users_dict[message['user']['account_name']] = client
                        self.database.user_login(message['user']['account_name'], client.getpeername()[0],
                                                 client.getpeername()[1], message['user']['pubkey'])
                        server_log.info(f'Присоединился клиент {message["user"]["account_name"]}')
                        self.answer_dict[client] = create_server_message(200)
                        change_count_connection = True
                    else:
                        try:
                            send_message(client, create_server_message(400, 'Неверный пароль.'))
                        except OSError:
                            pass
                        if client in self.r_list:
                            self.r_list.remove(client)
                        self.list_active_clients.remove(client)
                        client.close()
            # Обработка запроса на передачу сообщения другому пользователю
            elif 'action' in message and message['action'] == 'msg' and 'time' in message and 'to' in message and \
                    'from' in message and 'message' in message and 'encoding' in message:
                if message['to'] in self.users_dict:
                    server_log.info(f'Получено ссобщение {message["message"]} от клиента {message["from"]} '
                                    f'для клиента {message["to"]}')
                    self.answer_dict[client] = create_server_message(200)
                    self.answer_dict[self.users_dict[message['to']]] = message
                else:
                    server_log.info(f'Получено ссобщение {message["message"]} от клиента {message["from"]} для '
                                    f'клиента-offlain {message["to"]}')
                    self.answer_dict[client] = create_server_message(404)
            # обработка сообщения на получение списка всех пользователей
            elif 'action' in message and message['action'] == 'all_users' and 'time' in message and \
                    'user' in message and 'account_name' in message['user']:
                self.answer_dict[client] = create_server_message(202, self.database.all_users())
                server_log.info(f'Клиенту {message["user"]["account_name"]} отправлен список всех пользователей')
            # обработка сообщения на получение списка контактов
            elif 'action' in message and message['action'] == 'get_contacts' and 'time' in message and \
                    'user' in message and 'account_name' in message['user']:
                self.answer_dict[client] = create_server_message(202, self.database.get_contacts(
                    message["user"]["account_name"]))
                server_log.info(f'Клиенту {message["user"]["account_name"]} отправлен список контактов')
            # обработка сообщения на добовление контакта
            elif 'action' in message and message['action'] == 'add_contact' and 'time' in message and \
                    'user_id' in message and 'user_login' in message:
                answer = f'Пользователь {message["user_login"]} добавлен в список контактов пользователя {message["user_id"]}' \
                    if self.database.add_contact(message["user_id"], message["user_login"]) \
                    else f'Пользователь {message["user_login"]} уже есть в списке контактов пользователя {message["user_id"]}'
                self.answer_dict[client] = create_server_message(201, answer)
                server_log.info(answer)
            # обработка сообщения на удаление контакта
            elif 'action' in message and message['action'] == 'del_contact' and 'time' in message and \
                    'user_id' in message and 'user_login' in message:
                answer = f'Пользователь {message["user_login"]} удален из списка контактов пользователя {message["user_id"]}' \
                    if self.database.del_contact(message["user_id"], message["user_login"]) \
                    else f'Пользователя {message["user_login"]} нет в списке контактов пользователя {message["user_id"]}'
                self.answer_dict[client] = create_server_message(201, answer)
                server_log.info(answer)
            # Обработка сообщения на выход
            elif 'action' in message and message['action'] == 'quit' and 'time' in message and \
                    'user' in message and 'account_name' in message['user']:
                server_log.info(f'Клиент {message["user"]["account_name"]} инициировал отключение')
                self.database.user_logout(message["user"]["account_name"])
                self.list_active_clients.remove(client)
                if client in self.r_list:
                    self.r_list.remove(client)
                del self.users_dict[message['user']['account_name']]
                change_count_connection = True
            # Обработка неверных сообщений
            else:
                server_log.debug(f'Получено неверное сообщение')
                self.answer_dict[client] = create_server_message(400)

    @log()
    def send_answer(self):
        global change_count_connection
        while self.answer_dict:
            client, message = self.answer_dict.popitem()
            try:
                if client in self.w_list:
                    send_message(client, message)
                    server_log.info(f'Отправлено сообщение  {message} пользователю {client}')
                elif client not in self.w_list:
                    raise ConnectionError
            except (ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                server_log.error(f'Связь с клиентом с именем {client} была потеряна')
                for user in self.users_dict:
                    if self.users_dict[user] == client:
                        del self.users_dict[user]
                        break
                self.list_active_clients.remove(client)
                if client in self.w_list:
                    self.w_list.remove(client)
                change_count_connection = True


def main():
    server = WorkingServer()
    server.daemon = True
    server.start()
    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    def list_users_update():
        global change_count_connection
        if change_count_connection:
            main_window.active_clients_list.setModel(
                gui_create_model(server.database.get_active_users(), ['Пользователь']))
            main_window.active_clients_list.resizeColumnsToContents()
            main_window.active_clients_list.resizeRowsToContents()
            change_count_connection = False

    def show_user_history():
        global history_window
        history_window = HistoryWindow()
        history_window.history_table.setModel(gui_create_model(server.database.user_history(), ['Пользователь', ]))
        history_window.history_table.resizeColumnsToContents()
        history_window.history_table.resizeRowsToContents()

    def show_config_server():
        global config_window
        config_window = ConfigWindow()

    def show_register_user():
        global register_window
        register_window = RegisterWindow(server.database, server.socket)

    def show_remove_user():
        global remove_window
        remove_window = RemoveWindow(server.database, server.socket)

    list_users_update()

    timer = QTimer()
    timer.timeout.connect(list_users_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_users_update)
    main_window.show_history_button.triggered.connect(show_user_history)
    main_window.config_button.triggered.connect(show_config_server)
    main_window.register_button.clicked.connect(show_register_user)
    main_window.remove_button.clicked.connect(show_remove_user)
    main_window.config_button.triggered.connect(show_config_server)

    server_app.exec_()


if __name__ == "__main__":
    main()
