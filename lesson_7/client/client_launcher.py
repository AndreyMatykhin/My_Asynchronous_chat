import random
import subprocess

import client


def main():
    p_list = []
    while True:
        user = input("Запустить 10 клиентов (s) / Закрыть клиентов (x) / Выйти (q) ")
        if user == 'q':
            break
        elif user == 's':
            for _ in range(5):
                p_list.append(subprocess.Popen(f'python client.py 127.0.0.1 7777 {random.choice("rw")}',
                                               close_fds=True,
                                               shell=True))
            print(' Запущено 5 клиентов')
        elif user == 'x':
            for p in p_list:
                p.kill()
                p_list.remove(p)


if __name__ == "__main__":
    main()
