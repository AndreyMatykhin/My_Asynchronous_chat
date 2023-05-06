# 1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться
# доступность сетевых узлов. Аргументом функции является список, в котором каждый сетевой
# узел должен быть представлен именем хоста или ip-адресом. В функции необходимо
# перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
# («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с
# помощью функции ip_address().
import ipaddress
import subprocess
from pprint import pprint


def host_ping(hosts=list()):
    result = list()
    for host in hosts:
        try:
            host = ipaddress.ip_address(host)
        except ValueError:
            pass
        p = subprocess.Popen(f'ping {host} -c 2', shell=True, stdout=subprocess.PIPE)
        p.wait()
        result.append(f'Узел {host} {" не доступен" if p.returncode else " доступен"}')
    return result


if __name__ == "__main__":
    host_list = [
        '8.8.8.8',
        '127.0.0.1',
        'mail.cum'
    ]
    pprint(host_ping(host_list))
