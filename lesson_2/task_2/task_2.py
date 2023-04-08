# 2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с
# информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными. Для
# этого:
#   a. Создать функцию write_order_to_json(), в которую передается 5 параметров — товар
# (item), количество (quantity), цена (price), покупатель (buyer), дата (date). Функция
# должна предусматривать запись данных в виде словаря в файл orders.json. При
# записи данных указать величину отступа в 4 пробельных символа;
#   b. Проверить работу программы через вызов функции write_order_to_json() с передачей
# в нее значений каждого параметра.
import datetime
import json


def write_order_to_json(item='default', quantity=0, price=0, buyer='NoName', date=str(datetime.date.today())):
    with open('orders.json', 'r') as j_f_in:
        content = json.load(j_f_in)
    with open('orders.json', 'w') as j_f_out:
        content['orders'].append({'item': item,
                                  'quantity': quantity,
                                  'price': price,
                                  'buyer': buyer,
                                  'date': date})
        json.dump(content, j_f_out, indent=4, ensure_ascii=False)
        print(content)


if __name__ == "__main__":
    write_order_to_json()
