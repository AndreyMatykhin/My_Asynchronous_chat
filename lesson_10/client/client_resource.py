import dis

ACTION = [
    "presence",  # — присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online;
    "prоbe",  # — проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online;
    "msg",  # — простое сообщение пользователю или в чат;
    "quit",  # — отключение от сервера;
    "authenticate",  # — авторизация на сервере;
    "join",  # — присоединиться к чату;
    "leave"  # — покинуть чат.
]
ENCODING_MSG = 'ascii'


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(clsname, bases, clsdict)
