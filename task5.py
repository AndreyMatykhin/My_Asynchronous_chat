# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из
# байтовового в строковый тип на кириллице.
import subprocess

for site in ['yandex.ru', 'youtube.com']:
    for el in subprocess.Popen(['ping', '-c', '4', site], stdout=subprocess.PIPE).stdout:
        print(el.decode('utf-8'))

