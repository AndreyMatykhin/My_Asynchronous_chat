# 3. Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий
# сохранение данных в файле YAML-формата. Для этого:
#   a. Подготовить данные для записи в виде словаря, в котором первому ключу
# соответствует список, второму — целое число, третьему — вложенный словарь, где
# значение каждого ключа — это целое число с юникод-символом, отсутствующим в
# кодировке ASCII (например, €);
#   b. Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
# При этом обеспечить стилизацию файла с помощью параметра default_flow_style, а
# также установить возможность работы с юникодом: allow_unicode = True;
#   c. Реализовать считывание данных из созданного файла и проверить, совпадают ли они
# с исходными.
import yaml

LOAD_DATA = {'currency': ['US dollar', 'euro', 'рубль', 'pound sterling'],
             'total_number_of_bills': 1000,
             'number_of_currency_notes': {
                 '100 $': 150,
                 '50 €': 250,
                 '10 £': 600
             }
             }
with open('data_write_to_yaml.yaml', 'w') as file:
    yaml.dump(LOAD_DATA, file, default_flow_style=False, allow_unicode=True)
with open('data_write_to_yaml.yaml', 'r') as file:
    TEST_DATA = yaml.load(file, Loader=yaml.SafeLoader)
print(LOAD_DATA == TEST_DATA)
