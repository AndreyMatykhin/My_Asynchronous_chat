# 3.Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в
# байтовом типе.

words = ['attribute', 'класс', 'функция', 'type']
bad_words=[f'"{el}"' for el in words if not el.encode("ascii", "ignore").decode("ascii") == el]
print(f'Слова {", ".join(bad_words)} невозможно записать в байтовом типе')
