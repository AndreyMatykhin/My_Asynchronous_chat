# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из
# строкового представления в байтовое и выполнить обратное преобразование (используя
# методы encode и decode).

words = ['разработка', 'администрирование', 'protocol', 'standard']
new_words = [word.encode('utf-8') for word in words]
back_words = [word.decode('utf-8') for word in new_words]
print('Байтовое представление')
for word in new_words:
    print(type(word), word)
print('Обратное преобразование')
for word in back_words:
    print(type(word), word)
