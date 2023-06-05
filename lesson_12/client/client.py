import json
import random
import sys
import threading
import time
from socket import *

from client_storage import Storage
from log.client_log_config import client_log, log
from client_resource import ClientVerifier, ENCODING_MSG, send_message, get_message, send_presence_message, \
    send_get_all_users, send_get_contacts, send_add_contact, send_del_contact

username = f'Guest-{random.randint(0, 1000)}'
database_lock = threading.Lock()
my_socket_lock = threading.Lock()


class ClientTransmitter(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, user_name, socket, database):
        self.user_name = user_name
        self.socket = socket
        self.database = database
        super().__init__()

    def create_exit_message(self):
        return {"action": "quit",
                "time": time.time(),
                "user": {"account_name": self.user_name}
                }

    def send_client_message(self):
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
        self.database.save_message(client_message)

    def run(self):
        while True:
            print('Выберите действие: \n'
                  '\'message\' - отправить сообщение; \n'
                  '\'all_users\' - запросить список всех пользователей; \n'
                  '\'contacts\' - запросить список своих контактов; \n'
                  '\'add_contact\' - добавить пользователя в список своих контактов; \n'
                  '\'del_contact\' - удалить пользователя из списка своих контактов; \n'
                  '\'exit\' - выход')
            user_command = input('Ваша комманда: ')
            if user_command == 'exit':
                try:
                    send_message(self.socket, self.create_exit_message())
                except:
                    pass
                print('Завершение работы.')
                time.sleep(0.5)
                client_log.info("Завершение работы.")
                break
            elif user_command == 'message':
                self.send_client_message()
            elif user_command == 'all_users':
                print(self.database.all_users())
            elif user_command == 'contacts':
                print(self.database.all_contacts())
            elif user_command == 'add_contact':
                all_users = self.database.all_users()
                list_contacts = self.database.all_contacts()
                nickname = ''
                while nickname not in all_users:
                    nickname = input(
                        f'Кого из пользователей сервиса '
                        f'{", ".join([el for el in all_users if (el not in list_contacts and not el == self.user_name)])} '
                        f'вы хотите добавить в свой список контактов?')
                send_add_contact(self.socket, self.user_name, nickname)
            elif user_command == 'del_contact':
                list_contacts = send_get_contacts(self.socket, self.user_name)
                nickname = ''
                while nickname not in list_contacts:
                    nickname = input(
                        f'Кого из {", ".join(list_contacts)} вы хотите удалить из списка своих контактов?')
                send_del_contact(self.socket, self.user_name, nickname)


class ClientReceiver(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, user_name, socket, database):
        self.user_name = user_name
        self.socket = socket
        self.database = database
        super().__init__()

    def run(self):
        while True:
            time.sleep(1)
            # with Lock:
            try:
                g_message = get_message(self.socket)
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                client_log.critical(f'Потеряно соединение с сервером.')
                break
            else:
                self.database.save_message(g_message)
            # else:
            #     if 'action' in g_message and g_message[
            #         'action'] == 'msg' and 'time' in g_message and 'to' in g_message and \
            #             'from' in g_message and 'message' in g_message and 'encoding' in g_message:
            #         from_user = g_message["from"]
            #         text_message = g_message["message"]
            #         client_log.info(f'От пользователя "{from_user}" получено сообщение "{text_message}"')


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
        client_log.critical('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)
    try:
        username = sys.argv[3]
    except IndexError:
        client_log.debug(f'Вы неуказали имя пользователя при запуске. Для работы выбрано имя пользователя  {username}')
    create_socket = socket(AF_INET, SOCK_STREAM)
    try:
        create_socket.connect((addr, port))
    except OSError:
        client_log.critical("Проверьте правильность указанных адреса и порта")
        sys.exit(1)
    send_presence_message(create_socket, username)
    g_message = get_message(create_socket)["response"]
    while g_message == 409:
        client_log.info(f"Пользователь с именем '{username}' уже уже подключился к серверу.")
        print(f'Пользователь с именем {username} уже есть. \n'
              f'Введите новое имя или команду: \n '
              f'\'random\' - для автоматической генерации нового имени \n'
              f'\'exit\' - для выхода')
        user_command = input('Ваша комманда: ')
        if user_command == 'exit':
            client_log.info("Завершение работы.")
            print('Завершение работы.')
            time.sleep(0.5)
            break
        elif user_command == 'random':
            username = f'Guest-{random.randint(0, 1000)}'
            client_log.info(f"Ваше имя изменено на '{username}'")
        elif user_command:
            username = user_command
            client_log.info(f"Вы изменили имя на '{username}'")
        else:
            client_log.info(f"Вы не изменили имя '{username}. Попытка подключения будет повторена'")
        send_presence_message(create_socket, username)
        g_message = get_message(create_socket)["response"]
    if g_message == 200:
        client_log.info(f'Клиент запущен от пользователя {username}')
        return create_socket


def update_list_users_database(database, my_socket, user_name):
    all_users = send_get_all_users(my_socket, user_name)
    list_contacts = send_get_contacts(my_socket, user_name)
    database.add_all_users(all_users, list_contacts)
    client_log.info(f'Список пользователей мессенджера в базе обновлен')


def main():
    my_socket = create_connect()  # Создаем сокет
    print(my_socket, username)

    my_database = Storage(username)  # Создаем базу

    my_interface = ClientTransmitter(username, my_socket, my_database)  # Создаем транслятор
    my_interface.daemon = True
    my_interface.start()
    client_log.info('Запущены процессы')

    receiver = ClientReceiver(username, my_socket, my_database)  # Создаем поток-прослушиватель
    receiver.daemon = True
    receiver.start()
    update_list_users_database(my_database, my_socket, username)

    while True:
        time.sleep(1)
        if receiver.is_alive() and my_interface.is_alive():
            continue
        break


if __name__ == "__main__":
    main()
