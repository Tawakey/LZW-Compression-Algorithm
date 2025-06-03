import bitarray
from collections import deque  # used for queue
import copy
import os
import json

import bitarray.util

DEFAULT_MSG = """Алгоритм кодирования информации LZW
1. Выбрать файл
2. Закодировать
3. Декодировать
4. Просмотреть словарь
5. Собрать статистику
6. Выход
"""

STATISTIC_MSG = """- Исходный размер (файл {}): {} байт\n- Сжатый размер (файл output_binary.lzw): {} байт\n- Коэффициент сжатия: {}%"""

ALGORITHM = None


class Huffman:
    @staticmethod
    def encode(result_codes: list[int], encoded_dictionary, output_filename):
        max_freq = max(encoded_dictionary.values())
        dict_huffman_code = {k: max_freq-v for k, v in encoded_dictionary.items()}
        dict_to_code = {v: k for k, v in encoded_dictionary.items()}

        huffman_code = bitarray.util.huffman_code(dict_huffman_code)
        code_to_huffman = {k: huffman_code[v] for k, v in dict_to_code.items()}

        result = bitarray.bitarray()

        result.extend(bitarray.util.int2ba(len(result_codes), 4*8))
        for code in result_codes:
            coded_phrase = dict_to_code[code]

            result.extend(huffman_code[coded_phrase])

        Exporter.write_data_to_file(
            result,
            output_filename,
        )

        serialized_huffman_code = {v.to01(): k for k, v in code_to_huffman.items()}
        return serialized_huffman_code


class Exporter:
    @classmethod
    def write_data_to_file(cls, data, filename):
        if isinstance(data, dict):
            with open(filename, "w") as output:
                cls._write_json_data_to_file(data, output)
        if isinstance(data, bitarray.bitarray):
            with open(filename, "wb") as output:
                cls._write_data_to_binary_file(data, output)

    @classmethod
    def _write_json_data_to_file(cls, data: dict, file):
        json.dump(data, file)

    @classmethod
    def _write_data_to_binary_file(cls, data: bitarray.bitarray, file):
        data.tofile(file)


class BinaryFileReader:
    def __init__(self, filename):
        self.file = open(filename, "rb")

    def __iter__(self):
        return self

    def __next__(self):
        tmp = bitarray.bitarray()
        while True:
            try:
                tmp.fromfile(self.file, 1)
            except EOFError:
                raise StopIteration

            return tmp

    def reset(self):
        self.file.seek(0)

    def offset(self, offset):
        self.file.seek(offset)

    @staticmethod
    def read_from_binary_file(filename, count):
        with open(filename, "rb") as output:
            tmp = bitarray.bitarray()
            tmp.fromfile(output, count)
            return tmp


class FileReader:
    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        self.file = open(self.filename, "r", encoding="utf-8")
        return self

    def __next__(self):
        while True:
            char = self.file.read(1)
            if not char:
                raise StopIteration

            return char

    def reset(self):
        self.file.seek(0)

    @staticmethod
    def read_from_json(filename) -> dict:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)


class LZW:
    def __init__(self, filename: str):
        self.filename = filename

    def encode(self):
        self.initial_dictionary = {}
        index = 0

        file_reader = FileReader(self.filename)
        for char in file_reader:
            if char not in self.initial_dictionary:
                self.initial_dictionary[char] = index
                index += 1

        file_reader.reset()

        self.encoded_dictionary = copy.deepcopy(self.initial_dictionary)

        cur_string = deque()
        new_string = deque()
        result_codes = []
        for char in file_reader:
            new_string.append(char)

            if "".join(new_string) not in self.encoded_dictionary:
                result_codes.append(self.encoded_dictionary["".join(cur_string)])
                self.encoded_dictionary["".join(new_string)] = index
                index += 1
                cur_string.clear()
                cur_string.append(char)
                new_string = cur_string.copy()
            else:
                cur_string.append(char)

        result_codes.append(self.encoded_dictionary["".join(cur_string)])
        serialized_huffman_code = Huffman.encode(
            result_codes,
            self.encoded_dictionary,
            "output_binary.lzw"
        )

        to_write_json = {
            "initial": self.initial_dictionary,
            "huffman": serialized_huffman_code,
        }

        Exporter.write_data_to_file(to_write_json, "dictionary.json")
        print_to_menu("Кодирование прошло успешно")
        input()

    def decode(self):
        dictionary = FileReader.read_from_json("dictionary.json")

        huffman_code: dict = dictionary["huffman"]

        cur_bitseq = bitarray.bitarray()
        tmp = cur_bitseq
        codes = []
        cur_seq = ""
        size = BinaryFileReader.read_from_binary_file("output_binary.lzw", 4)
        size = bitarray.util.ba2int(size)
        cur_index = 0

        bin_file = BinaryFileReader("output_binary.lzw")
        bin_file.offset(4)
        for tmp in bin_file:
            for bit in tmp.to01():
                cur_seq += bit
                if cur_seq in huffman_code:
                    cur_index += 1
                    codes.append(huffman_code[cur_seq])
                    cur_seq = ""

                    if cur_index == size:
                        break
            if cur_index == size:
                break

        code_to_phrase = dictionary["initial"]
        code_to_phrase = {v: k for k, v in code_to_phrase.items()}

        index = max(code_to_phrase.keys())

        prev_seq = ""
        cur_seq = ""
        result_string = ""
        for code in codes:
            cur_seq = code_to_phrase[code]
            if prev_seq != "":
                index += 1
                code_to_phrase[index] = prev_seq + cur_seq[0]
            prev_seq = cur_seq
            result_string += cur_seq

        print_to_menu(result_string)
        input()

    def get_filename(self):
        return self.filename


def print_to_menu(msg: str):
    os.system("cls")
    print(msg)


def choose_file():
    global ALGORITHM
    print_to_menu("Введите название файла (формат .txt):")
    filename = input()
    if filename.endswith(".txt"):
        ALGORITHM = LZW(filename)
        print_to_menu("Файл выбран успешно")
        input()


def collect_info():
    origin_size = os.path.getsize(ALGORITHM.get_filename())
    compressed_size = os.path.getsize("output_binary.lzw")

    print_to_menu(STATISTIC_MSG.format(
        ALGORITHM.get_filename(),
        origin_size,
        compressed_size,
        round(compressed_size/origin_size * 100, 2)
    ))
    input()


if __name__ == "__main__":
    while True:
        print_to_menu(DEFAULT_MSG)
        variant = input()

        if variant == "1":
            choose_file()
        if variant == "2":
            if ALGORITHM is not None:
                ALGORITHM.encode()
        if variant == "3":
            if ALGORITHM is not None:
                ALGORITHM.decode()
        if variant == "4":
            print_to_menu(FileReader.read_from_json("dictionary.json"))
            input()
        if variant == "5":
            if ALGORITHM is not None:
                collect_info()
        if variant == "6":
            exit()
