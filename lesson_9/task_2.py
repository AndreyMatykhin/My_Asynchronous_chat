# 2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
# Меняться должен только последний октет каждого адреса. По результатам проверки должно
# выводиться соответствующее сообщение.
import ipaddress
from task_1 import host_ping


def host_range_ping():
    def input_ip_address(type_address: str):
        while True:
            try:
                return ipaddress.ip_address(input(f"Введите {type_address} ip-адрес"))
            except ValueError:
                pass

    while True:
        try:
            start_address = input_ip_address('начальный')
            finish_address = input_ip_address('конечный')
            if start_address >= finish_address:
                print(f'Начальный алресс не может быть больше конечного')
                raise ValueError
            elif not (str(start_address).split('.')[:3] == str(finish_address).split('.')[:3]):
                print(f'Введеные адреса не принадлежат одному диапазону')
                raise ValueError
            else:
                break
        except ValueError:
            pass
    list_address = []
    while start_address <= finish_address:
        list_address.append(str(start_address))
        start_address += 1
    return host_ping(list_address)


if __name__ == '__main__':
    print(host_range_ping())
