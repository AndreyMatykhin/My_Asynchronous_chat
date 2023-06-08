import datetime
import uuid

from sqlalchemy import create_engine, MetaData, Table, Column, String, ForeignKey, DateTime, Text, Integer, Boolean
from sqlalchemy.orm import registry, sessionmaker,relationship


class Storage:
    class User:
        def __init__(self, login: str, info='', onlain=True):
            self.login = login
            self.info = info
            self.onlain = onlain
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
                      Column('info', Text),
                      Column('onlain', Boolean)
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
        rez = self.session.query(self.User).filter_by(login=username)
        if rez.count():
            user = rez.first()
        else:
            user = self.User(username)
        self.session.add(user)
        self.session.commit()
        self.session.add(self.History(user.id, ip_address, port))
        self.session.commit()

    def all_users(self):
        return [el.login for el in self.session.query(self.User).all()]

    def get_contacts(self, username):
        user_id = self.session.query(self.User).filter(self.User.login == username).all()
        if user_id:
            user_id = [el.id for el in user_id]
            list_contact = [el.id_contact for el in
                            self.session.query(self.Contacts).filter(self.Contacts.id_user.in_(user_id)).all()] + [
                               el.id_user for el in
                               self.session.query(self.Contacts).filter(self.Contacts.id_contact.in_(user_id)).all()]
            return [el.login for el in self.session.query(self.User).filter(self.User.id.in_(list_contact)).all()]
        else:
            return []

    def add_contact(self, username, nickname):
        if not nickname in self.get_contacts(username):
            user_id, contact_id = tuple(
                el.id for el in self.session.query(self.User).filter(self.User.login.in_([username, nickname])).all())
            self.session.add(self.Contacts(user_id, contact_id))
            self.session.commit()
            return True
        else:
            return False

    def del_contact(self, username, nickname):
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
    print(my_storage.get_contacts('user1'))
    print(my_storage.add_contact('user1', 'user2'))
    print(my_storage.del_contact('user1', 'Guest-714'))
