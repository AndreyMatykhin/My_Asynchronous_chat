import datetime
import uuid

from sqlalchemy import create_engine, MetaData, Table, Column, String, ForeignKey, DateTime, Text, Integer
from sqlalchemy.orm import mapper, registry, sessionmaker


class Storage:
    class User:
        def __init__(self, login, info=''):
            self.login = login
            self.info = info
            self.id = None

    class History:
        def __init__(self, id_user, address, port):
            self.id_user = id_user
            self.date_time = None
            self.address = address
            self.port = port
            self.id = None

    class Contacts:
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
                      Column('info', Text)
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

    def user_login(self, username, ip_address, port):
        print(username, ip_address, port)
        rez = self.session.query(self.User).filter_by(login=username)
        print(type(rez))
        if rez.count():
            user = rez.first()
        else:
            user = self.User(username)
        self.session.add(user)
        self.session.commit()
        self.session.add(self.History(user.id, ip_address, port))
        self.session.commit()

    def all_users(self):
        return self.session.query(self.User.login).all()

    def user_history(self, login=None):
        query = self.session.query(self.User.login,
                                   self.History.date_time,
                                   self.History.address,
                                   self.History.port
                                   ).join(self.User)
        return query.filter(self.User.login == login).all() if login else query.all()


if __name__ == '__main__':
    my_storage = Storage()
    my_storage.user_login('user1', '127.0.0.1', 2345)
    my_storage.user_login('user2', '127.0.0.101', 3456)
    print(my_storage.all_users())
    print(my_storage.user_history('user2'))
    print(my_storage.user_history())
