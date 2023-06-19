import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSize, QRect, QMetaObject, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, qApp, QMainWindow, QComboBox, \
    QMessageBox

from log.client_log_config import client_log

logger = client_log


class WelcomeWindow(QDialog):
    '''
    Класс реализующий стартовый диалог с запросом логина и пароля
    пользователя.
    '''
    def __init__(self):
        super().__init__()
        self.ok = False

        self.setWindowTitle('Приветствуем!')
        self.setFixedSize(220, 170)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.label = QLabel('Введите имя пользователя:', self)
        self.label.move(10, 10)
        self.label.setFixedSize(200, 20)

        self.username = QLineEdit(self)
        self.username.setFixedSize(200, 20)
        self.username.move(10, 40)

        self.btn_ok = QPushButton('Начать', self)
        self.btn_ok.move(20, 130)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(120, 130)
        self.btn_cancel.clicked.connect(qApp.exit)

        self.label_passwd = QLabel('Введите пароль:', self)
        self.label_passwd.move(10, 70)
        self.label_passwd.setFixedSize(200, 20)

        self.client_passwd = QLineEdit(self)
        self.client_passwd.setFixedSize(200, 20)
        self.client_passwd.move(10, 100)
        self.client_passwd.setEchoMode(QLineEdit.Password)
        self.show()

    def click(self):
        '''Метод обрабтчик кнопки ОК.'''
        if self.username.text() and self.client_passwd.text():
            self.ok = True
            qApp.exit()


class MainWindow(QMainWindow):
    '''
    Класс - основное окно пользователя.
    Содержит всю основную логику работы клиентского модуля.
    '''
    def __init__(self, socket=None, database=None):
        super().__init__()
        self.socket = socket
        self.database = database

        self.setWindowTitle('Чат программа')
        self.setFixedSize(750, 530)
        self.setMinimumSize(QSize(750, 530))

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName('centralwidget')
        self.setCentralWidget(self.centralwidget)
        self.label_contacts = QLabel("Список контактов:", self.centralwidget)
        self.label_contacts.setGeometry(QRect(20, 0, 150, 20))
        self.label_history = QtWidgets.QLabel("История сообщений:", self.centralwidget)
        self.label_history.setGeometry(QRect(300, 0, 390, 20))
        self.label_new_message = QtWidgets.QLabel("Введите новое сообщение:", self.centralwidget)
        self.label_new_message.setGeometry(QRect(300, 330, 450, 20))
        self.list_contacts = QtWidgets.QListView(self.centralwidget)
        self.list_contacts.setGeometry(QRect(20, 25, 250, 410))
        self.list_contacts.doubleClicked.connect(self.select_user)
        self.list_messages = QtWidgets.QListView(self.centralwidget)
        self.list_messages.setGeometry(QRect(300, 25, 430, 300))
        self.list_messages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_messages.setWordWrap(True)
        self.text_message = QtWidgets.QTextEdit(self.centralwidget)
        self.text_message.setGeometry(QRect(300, 365, 430, 70))
        self.button_add_contact = QtWidgets.QPushButton("Добавить контакт", self.centralwidget)
        self.button_add_contact.setGeometry(QRect(20, 450, 170, 30))
        self.button_add_contact.clicked.connect(self.add_contact_window)
        self.button_remove_contact = QtWidgets.QPushButton("Удалить контакт", self.centralwidget)
        self.button_remove_contact.setGeometry(QRect(200, 450, 170, 30))
        self.button_remove_contact.clicked.connect(self.del_contact_window)
        self.button_send = QtWidgets.QPushButton("Отправить сообщение", self.centralwidget)
        self.button_send.setGeometry(QRect(380, 450, 170, 30))
        self.button_send.clicked.connect(self.send_message)
        self.button_clear = QtWidgets.QPushButton("Очистить поле", self.centralwidget)
        self.button_clear.setGeometry(QRect(560, 450, 170, 30))
        self.button_clear.clicked.connect(self.text_message.clear)

        self.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 756, 40))
        self.menu = QtWidgets.QMenu("Файл", self.menubar)
        self.menu_2 = QtWidgets.QMenu("Контакты", self.menubar)
        self.menu_2.addSeparator()
        self.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menu_exit = QtWidgets.QAction("Выход", self)
        self.menu.addAction(self.menu_exit)
        self.menu_exit.triggered.connect(qApp.exit)
        self.menu_add_contact = QtWidgets.QAction("Добавить контакт", self)
        self.menu_2.addAction(self.menu_add_contact)
        self.menu_add_contact.triggered.connect(self.add_contact_window)
        self.menu_del_contact = QtWidgets.QAction("Удалить контакт", self)
        self.menu_2.addAction(self.menu_del_contact)
        self.menu_del_contact.triggered.connect(self.del_contact_window)

        QMetaObject.connectSlotsByName(self)
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def send_message(self):
        '''Метод отправки сообщений'''
        message_text = self.text_message.toPlainText()
        self.text_message.clear()
        if not message_text:
            return
        try:
            self.socket.send_client_message(self.current_chat, message_text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
            self.close()
        else:
            logger.debug(f'Отправлено сообщение для {self.current_chat}: {message_text}')
            self.history_list_update()

    def add_contact_window(self):
        '''Метод создающий окно - диалог добавления контакта'''
        global select_dialog
        select_dialog = AddContactWindow(self.socket, self.database)
        select_dialog.button_ok.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        '''Метод обработчк нажатия кнопки "Добавить"'''
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        '''
        Метод добавляющий контакт в серверную и клиентсткую BD.
        После обновления баз данных обновляет и содержимое окна.
        '''
        try:
            self.socket.send_add_contact(new_contact)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            logger.info(f'Успешно добавлен контакт {new_contact}')
            self.messages.information(self, 'Успех', 'Контакт успешно добавлен.')

    def clients_list_update(self):
        '''Метод обновляющий список контактов.'''
        contacts_list = self.database.all_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.list_contacts.setModel(self.contacts_model)

    def del_contact_window(self):
        '''Метод создающий окно удаления контакта.'''
        global remove_dialog
        remove_dialog = DelContactWindow(self.database)
        remove_dialog.button_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        '''
        Метод удаляющий контакт из серверной и клиентсткой BD.
        После обновления баз данных обновляет и содержимое окна.
        '''
        selected = item.selector.currentText()
        try:
            self.socket.send_del_contact(selected)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.database.del_contact(selected)
            self.clients_list_update()
            logger.info(f'Успешно удалён контакт {selected}')
            self.messages.information(self, 'Успех', 'Контакт успешно удалён.')
            item.close()
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def select_user(self):
        '''Метод обработчик события двойного клика по списку контактов.'''
        self.current_chat = self.list_contacts.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        '''Метод активации чата с собеседником.'''
        self.label_new_message.setText(f'Введите сообщенние для {self.current_chat}:')
        self.button_clear.setDisabled(False)
        self.button_send.setDisabled(False)
        self.text_message.setDisabled(False)
        self.history_list_update()

    def set_disabled_input(self):
        ''' Метод делающий поля ввода неактивными'''
        self.label_new_message.setText('Для выбора получателя дважды кликните на нем в окне контактов.')
        self.text_message.clear()
        if self.history_model:
            self.history_model.clear()
        self.button_clear.setDisabled(True)
        self.button_send.setDisabled(True)
        self.text_message.setDisabled(True)

    def history_list_update(self):
        '''
        Метод заполняющий соответствующий QListView
        историей переписки с текущим собеседником.
        '''
        list = self.database.get_history_of_correspondence(self.current_chat)
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.list_messages.setModel(self.history_model)
        self.history_model.clear()
        length = len(list)
        start_index = 0
        if length > 20:
            start_index = length - 20
        for i in range(start_index, length):
            item = list[i]
            if item['from'] == self.current_chat:
                mess = QStandardItem(f'Входящее от {item["time"].replace(microsecond=0)}:\n {item["message"]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(f'Исходящее от {item["time"].replace(microsecond=0)}:\n {item["message"]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.list_messages.scrollToBottom()

    @pyqtSlot(str)
    def message(self, sender):
        '''
        Слот обработчик поступаемых сообщений, выполняет дешифровку
        поступаемых сообщений и их сохранение в истории сообщений.
        Запрашивает пользователя если пришло сообщение не от текущего
        собеседника. При необходимости меняет собеседника.
        '''
        if sender == self.current_chat:
            self.history_list_update()
        else:
            if self.database.check_contact(sender):
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}, открыть чат с ним?', QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                # Раз нету,спрашиваем хотим ли добавить юзера в контакты.
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}.\n '
                                          f'Данного пользователя нет в вашем контакт-листе.\n '
                                          f'Добавить в контакты и открыть чат с ним?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        '''
        Слот обработчик потери соеднинения с сервером.
        Выдаёт окно предупреждение и завершает работу приложения.
        '''
        self.messages.warning(self, 'Сбой соединения', 'Потеряно соединение с сервером. ')
        self.close()

    def make_connection(self, trans_obj):
        '''Метод обеспечивающий соединение сигналов и слотов.'''
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)


class AddContactWindow(QDialog):
    '''
    Диалог добавления пользователя в список контактов.
    Предлагает пользователю список возможных контактов и
    добавляет выбранный в контакты.
    '''
    def __init__(self, socket=None, database=None):
        super().__init__()
        self.socket = socket
        self.database = database
        self.setFixedSize(400, 90)
        self.setWindowTitle('Выберите контакт для добавления:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для добавления:', self)
        self.selector_label.setFixedSize(260, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(260, 20)
        self.selector.move(10, 25)

        self.button_refresh = QPushButton('Обновить список', self)
        self.button_refresh.setFixedSize(150, 30)
        self.button_refresh.move(65, 50)

        self.button_ok = QPushButton('Добавить', self)
        self.button_ok.setFixedSize(100, 30)
        self.button_ok.move(290, 10)

        self.button_cancel = QPushButton('Отмена', self)
        self.button_cancel.setFixedSize(100, 30)
        self.button_cancel.move(290, 50)
        self.button_cancel.clicked.connect(self.close)
        self.contacts_update_local()
        self.button_refresh.clicked.connect(self.contacts_update_from_server)

    def contacts_update_local(self):
        '''
        Метод заполнения списка возможных контактов.
        Создаёт список всех зарегистрированных пользователей
        за исключением уже добавленных в контакты и самого себя.
        '''
        self.selector.clear()
        self.selector.addItems(self.database.all_no_contact())

    def contacts_update_from_server(self):
        '''
        Метод обновления списка возможных контактов. Запрашивает с сервера
        список известных пользователей и обносляет содержимое окна.
         '''
        try:
            self.socket.update_list_users_database()
        except OSError:
            pass
        else:
            self.contacts_update_local()


class DelContactWindow(QDialog):
    '''
    Диалог удаления контакта. Прделагает текущий список контактов,
    не имеет обработчиков для действий.
    '''
    def __init__(self, database=None):
        super().__init__()
        self.database = database

        self.setFixedSize(400, 90)
        self.setWindowTitle('Выберите контакт для удаления:')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для удаления:', self)
        self.selector_label.setFixedSize(260, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(260, 20)
        self.selector.move(10, 25)

        self.button_ok = QPushButton('Удалить', self)
        self.button_ok.setFixedSize(100, 30)
        self.button_ok.move(290, 10)

        self.button_cancel = QPushButton('Отмена', self)
        self.button_cancel.setFixedSize(100, 30)
        self.button_cancel.move(290, 50)
        self.button_cancel.clicked.connect(self.close)

        # заполнитель контактов для удаления
        if database:
            self.selector.addItems(sorted(self.database.all_contacts()))


if __name__ == '__main__':
    test_app = QApplication(sys.argv)
    test_gui = WelcomeWindow()
    # test_gui = MainWindow()
    # my_database = Storage('user')
    # test_gui = AddContactWindow(database=my_database)
    # test_gui = AddContactWindow()
    test_gui.show()

    test_app.exec_()
