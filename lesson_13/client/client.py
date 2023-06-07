import argparse
import sys
import threading
from PyQt5.QtWidgets import QApplication

from client_storage import Storage
from client_gui import WelcomeWindow, MainWindow
from log.client_log_config import client_log, log
from client_resource import ClientSocket

database_lock = threading.Lock()
my_socket_lock = threading.Lock()


def get_start_parameters():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default='localhost', nargs='?')
    parser.add_argument('port', default=7777, type=int, nargs='?')
    parser.add_argument('name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.addr
    port = namespace.port
    user_name = namespace.name
    if not 1023 < port < 65536:
        client_log.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {port}. Допустимы адреса с 1024 до 65535. Клиент завершается.')
        exit(1)
    return addr, port, user_name


def main():
    ip_address, port, username = get_start_parameters()
    client_app = QApplication(sys.argv)
    if not username:
        start_dialog = WelcomeWindow()
        client_app.exec_()
        if start_dialog.ok:
            username = start_dialog.username.text()
            del start_dialog
        else:
            exit(0)
    my_database = Storage(username)  # Создаем базу

    my_interface = ClientSocket(ip_address, port, my_database, username)
    my_interface.daemon = True
    my_interface.start()
    main_window = MainWindow(my_interface, my_database)
    main_window.make_connection(my_interface)
    main_window.setWindowTitle(f'Чат Программа - {username}')
    client_app.exec_()
    my_interface.shutdown()
    my_interface.join()

if __name__ == "__main__":
    main()
