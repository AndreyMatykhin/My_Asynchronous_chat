import binascii
import datetime
import hashlib
import sys

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QLabel, QTableView, QPushButton, QDialog, \
    QLineEdit, QMessageBox, QComboBox


def gui_create_model(data_list, header=None):
    '''Функция заполняющий таблицу.'''
    result = QStandardItemModel()
    result.setHorizontalHeaderLabels(header if header else [])
    for row in data_list:
        if isinstance(row, str):
            result.appendRow(QStandardItem(row))
        else:
            result.appendRow(
                [QStandardItem(str(el.strftime('%Y-%m-%d %H:%M:%S')) if type(el) == datetime.datetime else str(el)) for
                 el in row])
    return result


class MainWindow(QMainWindow):
    '''Класс - основное окно сервера.'''

    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        self.setWindowTitle('Messaging Server')

        self.refresh_button = QAction('Обновить список', self)
        self.config_button = QAction('Настройки сервера', self)
        self.show_history_button = QAction('История клиентов', self)

        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        self.toolbar = self.addToolBar('MainMenu')
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_button)
        self.toolbar.addAction(exitAction)
        self.label = QLabel('Список всех клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 40)
        self.active_clients_list = QTableView(self)
        self.active_clients_list.move(10, 65)
        self.active_clients_list.setFixedSize(780, 400)
        self.register_button = QPushButton('Регистрация пользователя', self)
        self.register_button.setGeometry(QRect(10, 470, 270, 30))
        self.remove_button = QPushButton('Удаление пользователя', self)
        self.remove_button.setGeometry(QRect(290, 470, 270, 30))
        self.statusBar()
        self.show()


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)
        self.show()


class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Настройка сервера')
        self.setFixedSize(450, 250)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.db_path_label = QLabel('Путь до файла базы данных: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)
        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(260, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)
        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(280, 28)
        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)
        self.db_file = QLineEdit(self)
        self.db_file.move(280, 66)
        self.db_file.setFixedSize(160, 20)
        self.port_label = QLabel('Номер порта для соединений:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(220, 15)
        self.port = QLineEdit(self)
        self.port.move(280, 108)
        self.port.setFixedSize(160, 20)
        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(270, 15)
        self.ip_label_note = QLabel(
            'оставьте это поле пустым, чтобы принимать соединения \nс любых адресов.',
            self)
        self.ip_label_note.move(10, 170)
        self.ip_label_note.setFixedSize(440, 30)
        self.ip = QLineEdit(self)
        self.ip.move(280, 148)
        self.ip.setFixedSize(160, 20)
        self.save_button = QPushButton('Сохранить', self)
        self.save_button.move(160, 210)
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(280, 210)
        self.close_button.clicked.connect(self.close)
        self.show()


class RegisterWindow(QDialog):
    '''Класс диалог регистрации пользователя на сервере.'''

    def __init__(self, database, socket):
        super().__init__()
        self.database = database
        self.socket = socket
        self.setWindowTitle('Регистрация')
        self.setFixedSize(220, 183)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.label_username = QLabel('Введите имя пользователя:', self)
        self.label_username.move(10, 10)
        self.label_username.setFixedSize(200, 15)
        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(200, 20)
        self.client_name.move(10, 30)
        self.label_passwd = QLabel('Введите пароль:', self)
        self.label_passwd.move(10, 55)
        self.label_passwd.setFixedSize(200, 15)
        self.client_passwd = QLineEdit(self)
        self.client_passwd.setFixedSize(200, 20)
        self.client_passwd.move(10, 75)
        self.client_passwd.setEchoMode(QLineEdit.Password)
        self.label_conf = QLabel('Введите подтверждение:', self)
        self.label_conf.move(10, 100)
        self.label_conf.setFixedSize(200, 15)
        self.client_conf = QLineEdit(self)
        self.client_conf.setFixedSize(200, 20)
        self.client_conf.move(10, 120)
        self.client_conf.setEchoMode(QLineEdit.Password)
        self.button_ok = QPushButton('Сохранить', self)
        self.button_ok.move(10, 150)
        self.button_ok.clicked.connect(self.save_data)
        self.button_cancel = QPushButton('Выход', self)
        self.button_cancel.move(120, 150)
        self.button_cancel.clicked.connect(self.close)
        self.messages = QMessageBox()
        self.show()

    def save_data(self):
        '''
        Метод проверки правильности ввода и сохранения в базу нового пользователя.
        '''
        if not self.client_name.text():
            self.messages.critical(
                self, 'Ошибка', 'Не указано имя пользователя.')
            return
        elif self.client_passwd.text() != self.client_conf.text():
            self.messages.critical(
                self, 'Ошибка', 'Введённые пароли не совпадают.')
            return
        elif self.database.check_user(self.client_name.text()):
            self.messages.critical(
                self, 'Ошибка', 'Пользователь уже существует.')
            return
        else:
            passwd_bytes = self.client_passwd.text().encode('utf-8')
            salt = self.client_name.text().lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
            self.database.add_new_user(self.client_name.text(), binascii.hexlify(passwd_hash))
            self.messages.information(self, 'Успех', 'Пользователь успешно зарегистрирован.')
            # self.server.service_update_lists()
            self.close()


class RemoveWindow(QDialog):
    '''
    Класс - диалог выбора контакта для удаления.
    '''
    def __init__(self, database, socket):
        super().__init__()
        self.database = database
        self.socket = socket
        self.setFixedSize(350, 120)
        self.setWindowTitle('Удаление пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.selector_label = QLabel('Выберите пользователя для удаления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)
        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)
        self.button_ok = QPushButton('Удалить', self)
        self.button_ok.setFixedSize(100, 30)
        self.button_ok.move(230, 20)
        self.button_ok.clicked.connect(self.remove_user)
        self.button_cancel = QPushButton('Отмена', self)
        self.button_cancel.setFixedSize(100, 30)
        self.button_cancel.move(230, 60)
        self.button_cancel.clicked.connect(self.close)
        self.selector.addItems(self.database.all_users())
        self.show()

    def remove_user(self):
        '''Метод - обработчик удаления пользователя.'''
        self.database.rm_user(self.selector.currentText())
        self.close()


if __name__ == '__main__':
    test_app = QApplication(sys.argv)
    # test_gui = MainWindow()
    # test_gui.statusBar().showMessage('Test Statusbar Message')
    # test_list = QStandardItemModel(test_gui)
    # test_list = QStandardItemModel(test_gui)
    # test_list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    # test_list.appendRow([QStandardItem('user1'), QStandardItem('locolhost'), QStandardItem('3435'),
    #                      QStandardItem(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))])
    # test_list.appendRow([QStandardItem('user'), QStandardItem('localhost'), QStandardItem('6434'),
    #                      QStandardItem(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))])
    # test_gui.active_clients_list.setModel(test_list)
    # test_gui.active_clients_list.resizeColumnsToContents()
    test_app.exec_()
