# LZW алгоритм кодирования
## Задание
Составить бинарный код строки по алгоритму LZW согласно варианту номер  
```[((val – 1)mod16) + 1]```,   
где val – номер студента по списку группы в Moodle.

Словарь, кодовая последовательность и исходная строка должны храниться
в раздельных [если отдельно не оговорено – текстовых] файлах в одной
директории файловой системы.

Наборы данных, необходимые для
осуществления операций кодирования и декодирования, должны быть представлены в ней отдельными файлами. 

Файлы кодовой последовательности и исходной строки должны иметь один принцип (формат) записи и одну
кодировку при отображении.  

Сравнить с результатом кодирования согласно «начальному словарю».  

Рассчитать процент «сжатия» полученного алгоритмом LZW кода.

## Данные варианта №3
1. Для формирования вспомогательной строки должна использоваться "библиотечная очередь" с набором функций push(…), pop(…) и пр. или
аналогичных библиотечных/пользовательских;
2. Для хранения словаря должен использоваться формат .json;
3. Для хранения кодовой последовательности должны использоваться формат .bin;
4. Для формирования кодовой последовательности должен использоваться базовый алгоритм.

## Для запуска
В работе использована система сборки Make. Желательно предварительно создать виртуальное окружение
1. ```make prepare``` - установка библиотек из requirements.txt;
2. ```make run``` - запуск программы.

Для запуска необходим Python 3.9 и выше
