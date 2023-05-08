# 3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2. Но в данном
# случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать
# модуль tabulate). Таблица должна состоять из двух колонок и выглядеть примерно так:
# Reachable
# 10.0.0.1
# 10.0.0.2
#
# Unreachable
# 10.0.0.3
# 10.0.0.4
from tabulate import tabulate

from task_2 import host_range_ping


def host_range_ping_tab():
    host_list = host_range_ping()
    host_table = {'Reachable': [], 'Unreachable': []}
    for host in host_list:
        host = host.split(' ', 2)
        if host[2] == 'не доступен':
            host_table['Unreachable'].append(host[1])
        else:
            host_table['Reachable'].append(host[1])

    print(tabulate(host_table, headers='keys', tablefmt="pipe", stralign="center"))


if __name__ == '__main__':
    host_range_ping_tab()
