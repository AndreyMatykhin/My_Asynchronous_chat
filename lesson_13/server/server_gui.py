import datetime
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QLabel, QTableView, QPushButton, QDialog


def gui_create_model(data_list, header=None):
    result = QStandardItemModel()
    result.setHorizontalHeaderLabels(header if header else [])
    for row in data_list:
        if isinstance(row,str):
            result.appendRow(QStandardItem(row))
        else:
            result.appendRow(
            [QStandardItem(str(el.strftime('%Y-%m-%d %H:%M:%S')) if type(el) == datetime.datetime else str(el)) for el in row])
    return result


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройки геометрии основного окна
        self.setFixedSize(800, 600)
        self.setWindowTitle('Messaging Server')
        # Кнопка обновить список клиентов
        self.refresh_button = QAction('Обновить список', self)
        # Кнопка настроек сервера
        self.config_btn = QAction('Настройки сервера', self)
        # Кнопка вывести историю сообщений
        self.show_history_button = QAction('История клиентов', self)
        # Кнопка выхода
        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)
        # Тулбар
        self.toolbar = self.addToolBar('MainMenu')
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addAction(exitAction)
        # Надпись о том, что ниже список подключённых клиентов
        self.label = QLabel('Список всех клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 40)
        # Окно со списком подключённых клиентов.
        self.active_clients_list = QTableView(self)
        self.active_clients_list.move(10, 65)
        self.active_clients_list.setFixedSize(780, 400)

        self.statusBar()
        self.show()


class HistoryWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройки окна:
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Кнапка закрытия окна
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        # Лист с собственно историей
        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()

class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Настройки окна:
        self.setWindowTitle('Настройка сервера')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.show()

if __name__ == '__main__':
    test_app = QApplication(sys.argv)
    test_gui = MainWindow()
    test_gui.statusBar().showMessage('Test Statusbar Message')
    test_list = QStandardItemModel(test_gui)
    test_list = QStandardItemModel(test_gui)
    test_list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
    test_list.appendRow([QStandardItem('user1'), QStandardItem('locolhost'), QStandardItem('3435'),
                         QStandardItem(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))])
    test_list.appendRow([QStandardItem('user'), QStandardItem('localhost'), QStandardItem('6434'),
                         QStandardItem(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))])
    test_gui.active_clients_list.setModel(test_list)
    test_gui.active_clients_list.resizeColumnsToContents()
    test_app.exec_()
