# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в
# последовательность кодов (не используя методы encode и decode) и определить тип,
# содержимое и длину соответствующих переменных.


word = {'class': b'\x63\x6c\x61\x73\x73',
        'function': b'\x66\x75\x6e\x63\x74\x69\x6f\x6e',
        'method': b'\x6d\x65\x74\x6f\x64'}
for el in word:
    print(f'тип элемента: {type(word[el])}, содержимое: {word[el]}, длина: {len(word[el])}')
