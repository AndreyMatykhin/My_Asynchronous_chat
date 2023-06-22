import datetime
import uuid

from sqlalchemy import create_engine, MetaData, Table, Column, String, ForeignKey, DateTime, Text, Integer, Boolean
from sqlalchemy.orm import registry, sessionmaker, relationship


class Storage:
    '''
    Класс - оболочка для работы с базой данных сервера.
    Использует SQLite базу данных, реализован с помощью SQLAlchemy ORM и используется классический подход.
    '''
    class User:
        '''Класс - отображение таблицы всех пользователей.'''
        def __init__(self, login: str, hash_passwd: str):
            self.login = login
            self.hash_passwd = hash_passwd
            self.key = None
            self.is_active = None
            self.id = None

    class History:
        '''Класс - отображение таблицы истории входов.'''
        def __init__(self, id_user, address, port):
            self.id_user = id_user
            self.date_time = None
            self.address = address
            self.port = port
            self.id = None

    class Contacts:
        '''Класс - отображение таблицы контактов пользователей.'''
        def __init__(self, id_user, id_contact):
            self.id_user = id_user
            self.id_contact = id_contact
            self.id = None

    def __init__(self):
        self.my_engine = create_engine('sqlite:///base_of_server.db3', echo=False, pool_recycle=7200)
        self.metadata = MetaData()
        self.registry = registry()
        users = Table('Users', self.metadata,
                      Column('id', String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True),
                      Column('login', String(length=36), unique=True),
                      Column('hash_passwd', String),
                      Column('key', Text),
                      Column('is_active', Boolean)
                      )
        history_users = Table('History_users', self.metadata,
                              Column('id', String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True),

                              Column('id_user', ForeignKey('Users.id')),
                              Column('date_time', DateTime, default=datetime.datetime.now()),
                              Column('address', String),
                              Column('port', Integer))
        list_contacts = Table('List_contacts', self.metadata,
                              Column('id', String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True),
                              Column('id_user', ForeignKey('Users.id')),
                              Column('id_contact', ForeignKey('Users.id')))
        self.metadata.create_all(self.my_engine)
        self.registry.map_imperatively(self.User, users)
        self.registry.map_imperatively(self.History, history_users)
        self.registry.map_imperatively(self.Contacts, list_contacts)
        my_session = sessionmaker(bind=self.my_engine)
        self.session = my_session()

    def check_user(self, username):
        '''Метод проверяющий существование пользователя.'''
        return True if self.session.query(self.User).filter_by(login=username).count() else False

    def user_login(self, username, ip_address, port, key):
        '''
        Метод выполняющийся при входе пользователя, записывает в базу факт входа
        Обновляет открытый ключ пользователя при его изменении.
        '''
        rez = self.session.query(self.User).filter_by(login=username)
        if rez.count():
            user = rez.first()
            if user.key != key:
                user.key = key
        else:
            raise ValueError('Пользователь не зарегистрирован.')
        user.is_active = True
        self.session.add(self.History(user.id, ip_address, port))
        self.session.commit()

    def user_logout(self, username):
        '''Метод фиксирующий отключения пользователя.'''
        rez = self.session.query(self.User).filter_by(login=username)
        if rez.count():
            if rez.first().is_active:
                rez.first().is_active = False
                self.session.commit()
            else:
                raise ValueError('Пользователь уже вышел.')
        else:
            raise ValueError('Пользователь не зарегистрирован.')

    def add_new_user(self, username, hash_passwd):
        '''
        Метод регистрации пользователя.
        Принимает имя и хэш пароля, создаёт запись в таблице статистики.
        '''
        if self.check_user(username):
            raise ValueError('Пользователь уже зарегистрирован.')
        self.session.add(self.User(login=username, hash_passwd=hash_passwd))
        self.session.commit()

    def rm_user(self, username):
        '''Метод удаляющий пользователя из базы.'''
        if self.check_user(username):
            user = self.session.query(self.User).filter_by(login=username).first()
            self.session.query(self.History).filter_by(id_user=user.id).delete()
            self.session.query(self.Contacts).filter(
                (self.Contacts.id_user == user.id) | (self.Contacts.id_contact == user.id)).delete()
            self.session.query(self.User).filter_by(login=username).delete()
        return True if self.session.commit() else False

    def get_hash_passwd(self, username):
        '''Метод получения хэша пароля пользователя.'''
        rez = self.session.query(self.User).filter_by(login=username)
        return rez.first().hash_passwd if rez.count() else None

    def get_key(self, username):
        '''Метод получения публичного ключа пользователя.'''
        rez = self.session.query(self.User).filter_by(login=username)
        return rez.first().key if rez.count() else None

    def all_users(self):
        '''Метод возвращающий список известных пользователей.'''
        return [el.login for el in self.session.query(self.User).all()]

    def get_active_users(self):
        '''Метод возвращающий список активных пользователей.'''
        return [el.login for el in self.session.query(self.User).filter_by(is_active=True).all()]

    def get_contacts(self, username):
        '''Метод возвращающий список контактов пользователя.'''
        rez = self.session.query(self.User).filter_by(login=username)
        if rez.count():
            list_contact = [el.id_contact for el in
                            self.session.query(self.Contacts).filter(self.Contacts.id_user == rez.first().id).all()] + \
                           [el.id_user for el in
                            self.session.query(self.Contacts).filter(self.Contacts.id_contact == rez.first().id).all()]
            return [el.login for el in self.session.query(self.User).filter(self.User.id.in_(list_contact)).all()]
        else:
            return []

    def add_contact(self, username, nickname):
        '''Метод добавления контакта для пользователя.'''
        if nickname not in self.get_contacts(username):
            user_id, contact_id = tuple(
                el.id for el in self.session.query(self.User).filter(self.User.login.in_([username, nickname])).all())
            self.session.add(self.Contacts(user_id, contact_id))
            self.session.commit()
            return True
        else:
            return False

    def del_contact(self, username, nickname):
        '''Метод удаления контакта пользователя.'''
        user = self.session.query(self.User).filter(self.User.login == username).all()
        nik = self.session.query(self.User).filter(self.User.login == nickname).all()
        if nik:
            self.session.query(self.Contacts).filter(
                (self.Contacts.id_user == user[0].id and self.Contacts.id_contact == nik[0].id) or (
                        self.Contacts.id_user == nik[0].id and self.Contacts.id_contact == user[0].id)).delete()
            self.session.commit()
            return True
        else:
            return False

    def user_history(self, login=None):
        '''Метод возвращающий историю входов.'''
        query = self.session.query(self.User.login,
                                   self.History.date_time,
                                   self.History.address,
                                   self.History.port
                                   ).join(self.User)
        return query.filter(self.User.login == login).all() if login else query.all()


if __name__ == '__main__':
    my_storage = Storage()
    # my_storage.add_new_user('user1', 'asdfg')
    my_storage.user_login('user1', '127.0.0.1', 2345, 'asdfghh')
    my_storage.user_login('user2', '127.0.0.1', 3345, 'asdfghh')
    # my_storage.user_login('user2', '127.0.0.101', 3456)
    # print(my_storage.all_users())
    # print(my_storage.user_history('user2'))
    # print(my_storage.user_history())
    # print(my_storage.get_contacts('user1'))
    print(my_storage.add_contact('user2', 'user1'))
    # print(my_storage.del_contact('user1', 'Guest-714'))
    print(my_storage.check_user('user1'))
    print(my_storage.get_contacts('user1'), my_storage.get_contacts('user2'))
    print(my_storage.all_users())
    # my_storage.rm_user('user1')
    print(my_storage.get_key('user1'), my_storage.get_passwd('user2'))
    print(my_storage.get_active_users())
    my_storage.user_logout('user1')
    print(my_storage.get_active_users())
