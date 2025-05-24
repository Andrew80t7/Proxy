import math
import os
from datetime import datetime
from http.server import (SimpleHTTPRequestHandler,
                         HTTPServer)
from typing import List, Union
import re

DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")
if not os.path.exists(DUMP_DIR):
    os.makedirs(DUMP_DIR)


class DumpRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DUMP_DIR, **kwargs)


def run_dump_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, DumpRequestHandler)
    print(f"Dump download server running on port {port}...")
    httpd.serve_forever()


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def sum_numbers(numbers: list) -> float:
    return sum(numbers)


def celsius_to_kelvin(temp: float) -> float:
    return temp + 273.15


def lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b) if a and b else 0


# Строковые операции
def count_consonants(s: str) -> int:
    consonants = 'bcdfghjklmnpqrstvwxyz'
    return sum(1 for char in s.lower() if char in consonants)


def remove_whitespace(s: str) -> str:
    return (s.replace(" ", "").
            replace("\t", "").
            replace("\n", ""))


def rot13(s: str) -> str:
    return s.translate(str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWX'
        'YZabcdefghijklmnopqrstuvwxyz',
        'NOPQRSTUVWXYZABCDEFGHIJK'
        'LMnopqrstuvwxyzabcdefghijklm'
    ))


def count_substrings(s: str, sub: str) -> int:
    return s.count(sub)


# Работа с датами
def is_weekend(date_str: str) -> bool:
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.weekday() >= 5


def get_century(year: int) -> int:
    return (year - 1) // 100 + 1


# Валидация данных
def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def is_strong_password(password: str) -> bool:
    return (
            len(password) >= 8 and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*" for c in password)
    )


# Геометрические расчеты
def triangle_area(base: float, height: float) -> float:
    return 0.5 * base * height


def circle_circumference(radius: float) -> float:
    return 2 * math.pi * radius


# Преобразования
def minutes_to_hours(minutes: Union[int, float]) -> float:
    return minutes / 60


def kg_to_pounds(kg: float) -> float:
    return kg * 2.20462


# Работа со списками
def flatten_list(nested_list: list) -> list:
    return [item for sublist in nested_list for item in sublist]


def remove_duplicates(lst: list) -> list:
    return list(dict.fromkeys(lst))


# Бинарные операции
def decimal_to_binary(n: int) -> str:
    return bin(n)[2:]


def binary_to_decimal(binary: str) -> int:
    return int(binary, 2)


# Рекурсивные функции
def sum_digits(n: int) -> int:
    return (abs(n) % 10 +
            + sum_digits(abs(n) //
                         10)) if n else 0


def recursive_factorial(n: int) -> int:
    return 1 if n <= 1 else n * recursive_factorial(n - 1)


# Генераторы данных
def generate_primes(n: int) -> List[int]:
    sieve = [True] * (n + 1)
    for i in range(2, int(math.sqrt(n)) + 1):
        if sieve[i]:
            sieve[i * i: n + 1: i] = [False] * len(sieve[i * i: n + 1: i])
    return [i
            for i, IS_PRIME in enumerate(sieve) if IS_PRIME and i >= 2]


# Статистика
def calculate_variance(data: List[float]) -> float:
    mean = sum(data) / len(data)
    return sum((x - mean) ** 2 for x in data) / len(data)


# Фильтрация
def filter_even(numbers: List[int]) -> List[int]:
    return [n for n in numbers if n % 2 == 0]


# Валидация чисел
def is_perfect_square(n: int) -> bool:
    return math.isqrt(n) ** 2 == n


# Шифрование
def caesar_cipher(text: str, shift: int) -> str:
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)


# Физические расчеты
def calculate_kinetic_energy(mass: float, velocity: float) -> float:
    return 0.5 * mass * velocity ** 2


# Проверка последовательностей
def is_arithmetic_sequence(sequence: List[Union[int, float]]) -> bool:
    if len(sequence) < 2:
        return True
    diff = sequence[1] - sequence[0]
    return all(sequence[i + 1] -
               sequence[i] == diff for i in range(len(sequence) - 1))


# Работа с файлами
def count_lines(filename: str) -> int:
    with open(filename, 'r') as file:
        return sum(1 for _ in file)


def is_even(n: int) -> bool:
    """Проверяет чётность числа"""
    return n % 2 == 0


def sum_list(numbers: list) -> float:
    """Возвращает сумму элементов списка"""
    return sum(numbers)


def km_to_miles(km: float) -> float:
    """Конвертирует километры в мили"""
    return km * 0.621371


def is_leap_year(year: int) -> bool:
    """Проверяет високосный год"""
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 == 0:
        return True
    else:
        return False


def find_max(numbers: list) -> float:
    """Находит максимальное число в списке"""
    return max(numbers) if numbers else None


def count_words(text: str) -> int:
    """Считает количество слов в строке"""
    return len(text.split())


def is_pangram(s: str) -> bool:
    """Проверяет панграмму (содержит все буквы алфавита)"""
    alphabet = set('abcdefghijklmnopqrstuvwxyz')
    return alphabet.issubset(s.lower())


def circle_area(radius: float) -> float:
    """Вычисляет площадь круга"""
    if radius < 0:
        raise ValueError("Радиус не может быть отрицательным")
    return 3.14159 * radius ** 2


def time_to_seconds(hours: int, minutes: int) -> int:
    """Конвертирует часы и минуты в секунды"""
    if hours < 0 or minutes < 0:
        raise ValueError("Время не может быть отрицательным")
    return hours * 3600 + minutes * 60


def is_prime_v2(n: int) -> bool:
    """Альтернативная проверка простого числа"""
    if n <= 1:
        return False
    return all(n % i != 0 for i in range(2,
                                         int(n ** 0.5) + 1))


if __name__ == "__main__":
    run_dump_server(8000)
