# 1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку
# определенных данных из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый
# «отчетный» файл в формате CSV. Для этого:
#   a. Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с
# данными, их открытие и считывание данных. В этой функции из считанных данных
# необходимо с помощью регулярных выражений извлечь значения параметров
# «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения
# каждого параметра поместить в соответствующий список. Должно получиться четыре
# списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же
# функции создать главный список для хранения данных отчета — например, main_data
# — и поместить в него названия столбцов отчета в виде списка: «Изготовитель
# системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих
# столбцов также оформить в виде списка и поместить в файл main_data (также для
# каждого файла);
#   b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой
# функции реализовать получение данных через вызов функции get_data(), а также
# сохранение подготовленных данных в соответствующий CSV-файл;
#   c. Проверить работу программы через вызов функции write_to_csv().

import re
import csv
import chardet
from pathlib import Path


def get_data(file_mask='info*.txt'):
    file_list = list(map(str, Path('.').glob(file_mask)))
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    for file in file_list:
        encoding = chardet.detect(open(file, 'rb').read())['encoding']
        with open(file, 'r', encoding=encoding) as f:
            f_obg = f.read()
            os_name_list.append(re.compile(r'Название ОС:\s*(.*)').search(f_obg)[1])
            os_prod_list.append(re.compile(r'Изготовитель ОС:\s*(.*)').search(f_obg)[1])
            os_code_list.append(re.compile(r'Код продукта:\s*(.*)').search(f_obg)[1])
            os_type_list.append(re.compile(r'Тип системы:\s*(.*)').search(f_obg)[1])
    main_data = [["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]]
    for i in range(len(file_list)):
        main_data.append([os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]])
    return main_data


def write_to_csv(file_name='result.csv'):
    with open(file_name, 'w', encoding='utf-8') as f:
        f_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        for row in get_data():
            f_writer.writerow(row)


if __name__ == "__main__":
    write_to_csv('task_1_result.csv')
