import dis

ANSWER = {
    # 1xx — информационные сообщения:
    100: 'базовое уведомление',
    101: 'важное уведомление',
    # 2xx — успешное завершение:
    200: 'OK',
    201: '(created) — объект создан',
    202: '(accepted) — подтверждение',
    # 4xx — ошибка на стороне клиента:
    400: 'неправильный запрос/JSON-объект',
    401: 'не авторизован',
    402: 'неправильный логин/пароль',
    403: '(forbidden) — пользователь заблокирован',
    404: '(not found) — пользователь/чат отсутствует на сервере',
    409: '(conflict) — уже имеется подключение с указанным логином',
    410: '(gone) — адресат существует, но недоступен (offline)',
    # 5xx — ошибка на стороне сервера:
    500: 'ошибка сервера.'
}
ACTION=[
    "presence", # — присутствие. Сервисное сообщение для извещения сервера о присутствии клиента online;
    "prоbe",# — проверка присутствия. Сервисное сообщение от сервера для проверки присутствии клиента online;
    "msg",# — простое сообщение пользователю или в чат;
    "quit",# — отключение от сервера;
    "authenticate",# — авторизация на сервере;
    "join",# — присоединиться к чату;
    "leave" #— покинуть чат.
    ]

class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        attrs = []
        for func in clsdict:
            try:
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for i in ret:
                    print(i)
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            attrs.append(i.argval)
        print(methods,attrs)
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        if not ('SOCK_STREAM' in methods and 'AF_INET' in methods):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(clsname, bases, clsdict)