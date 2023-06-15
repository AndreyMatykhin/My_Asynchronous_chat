import uuid
import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, String, ForeignKey, Integer, DateTime, JSON, Text, \
    Boolean
from sqlalchemy.orm import registry, sessionmaker

from client_resource import ANSWER


class Storage:
    '''
    Класс - оболочка для работы с базой данных клиента.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется классический подход.
    '''

    class ListUsers:
        '''Класс - отображение для таблицы всех пользователей.'''

        def __init__(self, login, is_contact=False):
            self.login = login
            self.is_contact = is_contact
            self.id = None

    class InputServesMessage:
        '''Класс - отображение таблицы входящих сервесных сообщений.'''

        def __init__(self, code, alert=''):
            self.code = code
            self.alert = alert
            self.time = None
            self.id = None

    class OutputServesMessage:
        '''Класс - отображения таблицы исходящих сервесных сообщений.'''

        def __init__(self, action, time, option):
            self.action = action
            self.time = time
            self.option = option
            self.id = None

    class UserMessageHistory:
        '''Класс - отображения пользовательских сообщений.'''

        def __init__(self, time, to_name, from_name, encoding, message):
            self.time = datetime.datetime.fromtimestamp(time)
            self.to_name = to_name
            self.from_name = from_name
            self.encoding = encoding
            self.message = message
            self.id = None

    def __init__(self, username):
        self.my_engine = create_engine(f'sqlite:///base_of_client_{username}.db3', echo=False, pool_recycle=7200,
                                       connect_args={'check_same_thread': False})
        self.metadata = MetaData()
        self.username = username
        self.registry = registry()
        list_users = Table('List_users', self.metadata,
                           Column('id', String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True),
                           Column('login', String(length=36), unique=True),
                           Column('is_contact', Boolean))
        input_serves_message = Table('Input_serves_message', self.metadata,
                                     Column('id', String(length=36), default=lambda: str(uuid.uuid4()),
                                            primary_key=True),
                                     Column('code', Integer),
                                     Column('time', DateTime, default=lambda: datetime.datetime.now()),
                                     Column('alert', String))
        output_serves_message = Table('Output_serves_message', self.metadata,
                                      Column('id', String(length=36), default=lambda: str(uuid.uuid4()),
                                             primary_key=True),
                                      Column('action', String),
                                      Column('time', DateTime),
                                      Column('option', JSON))
        user_message_history = Table('User_message_history', self.metadata,
                                     Column('id', String(length=36), default=lambda: str(uuid.uuid4()),
                                            primary_key=True),
                                     Column('time', DateTime),
                                     Column('to_name', ForeignKey('List_users.login')),
                                     Column('from_name', ForeignKey('List_users.login')),
                                     Column('encoding', String),
                                     Column('message', Text))
        self.metadata.create_all(self.my_engine)
        self.registry.map_imperatively(self.ListUsers, list_users)
        self.registry.map_imperatively(self.InputServesMessage, input_serves_message)
        self.registry.map_imperatively(self.OutputServesMessage, output_serves_message)
        self.registry.map_imperatively(self.UserMessageHistory, user_message_history)
        my_session = sessionmaker(bind=self.my_engine)
        self.session = my_session()

    def add_all_users(self, list_users: list, list_contact: list):
        '''Метод добавления в таблюцу списка пользователей и списка контактов.'''
        self.session.query(self.ListUsers).delete()
        for el in list_users:
            self.session.add(self.ListUsers(el, el in list_contact))
            self.session.commit()

    def add_contact(self, nickname):
        '''Метод добаввления пользователя в список контактов'''
        self.session.query(self.ListUsers).filter(self.ListUsers.login == nickname).one().is_contact = True
        self.session.commit()

    def del_contact(self, nickname):
        '''Метод удаления пользователя из списка котактов.'''
        self.session.query(self.ListUsers).filter(self.ListUsers.login == nickname).one().is_contact = False
        self.session.commit()

    def all_contacts(self):
        '''Метод получения списка контактов.'''
        return [el.login for el in
                self.session.query(self.ListUsers).filter(
                    not self.ListUsers.login == self.username and self.ListUsers.is_contact).order_by(
                    self.ListUsers.login).all()]

    def all_users(self):
        '''Метод получения списка всех полользователей.'''
        return [el.login for el in
                self.session.query(self.ListUsers).filter(not self.ListUsers.login == self.username).order_by(
                    self.ListUsers.login).all()]

    def all_no_contact(self):
        '''Метод получения списка пользователей не входящих в списко контактов.'''
        return [el.login for el in
                self.session.query(self.ListUsers).filter(self.ListUsers.login != self.username,
                                                          self.ListUsers.is_contact.isnot(True)).order_by(
                    self.ListUsers.login).all()]

    def save_message(self, message: dict):
        '''Метод сохранения пользлвательских сообщений в базе.'''
        if 'action' in message and message['action'] == 'msg' and 'time' in message and 'to' in message and \
                'from' in message and 'message' in message and 'encoding' in message:
            self.session.add(self.UserMessageHistory(message["time"],
                                                     message["to"],
                                                     message["from"],
                                                     message["encoding"],
                                                     message["message"]))
            self.session.commit()
        elif 'response' in message and message['response'] in ANSWER and 'alert' in message:
            self.session.add(self.InputServesMessage(message['response'], message['alert']))
            self.session.commit()
        else:
            return False
        return True

    def get_serves_message(self, code, time_marker):
        '''Метод получения из базы сервесных сообщений по коду и времени'''
        return [el.alert for el in self.session.query(self.InputServesMessage).filter(
            self.InputServesMessage.code == code, self.InputServesMessage.time >= time_marker).order_by(
            self.InputServesMessage.time).all()][0]

    def get_history_of_correspondence(self, nickname):
        '''Метод получения из базы истории переписки с другим пользователем.'''
        return [
            {"time": el.time,
             "to": el.to_name,
             "from": el.from_name,
             "encoding": el.encoding,
             "message": el.message}
            for el in self.session.query(self.UserMessageHistory).filter(
                (self.UserMessageHistory.to_name == nickname) | (
                        self.UserMessageHistory.from_name == nickname)).order_by(
                self.UserMessageHistory.time).all()]

    def check_contact(self, nickname):
        '''Мметод проверки наличия пользователя в списке контактов.'''
        return self.session.query(self.ListUsers).filter(self.ListUsers.login == nickname).one().is_contact


if __name__ == '__main__':
    my_storage = Storage('user')
    # my_storage.add_all_users(['user', 'user1', 'Guest-714'], ['user1'])
    print(my_storage.all_users())
    print(my_storage.all_contacts())
    print(my_storage.all_no_contact())
    # print(my_storage.save_message(
    #     {'action': 'msg', 'time': 1685673629.9949906, 'to': 'user', 'from': 'user1', 'encoding': 'ascii',
    #      'message': 'Привет'}))
    # print(my_storage.all_users())
    for el in my_storage.get_history_of_correspondence('user'):
        print(el)
