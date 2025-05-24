import math
import os
from http.server import (SimpleHTTPRequestHandler,
                         HTTPServer)

DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")
if not os.path.exists(DUMP_DIR):
    os.makedirs(DUMP_DIR)


class DumpRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         directory=DUMP_DIR,
                         **kwargs)


def run_dump_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address,
                       DumpRequestHandler)
    print(f"Dump download server running on port"
          f" {port}...")
    httpd.serve_forever()


def is_even(n: int) -> bool:
    """Проверяет четность числа"""
    return n % 2 == 0


def count_vowels(s: str) -> int:
    """Считает количество гласных букв в строке"""
    vowels = 'aeiouAEIOUауоыиэяюёеАУОЫИЭЯЮЁЕ'
    return sum(1 for char in s if char in vowels)


def reverse_string(s: str) -> str:
    """Возвращает обратную строку"""
    return s[::-1]


def is_palindrome(s: str) -> bool:
    """Проверяет является ли строка палиндромом"""
    s = ''.join(filter(str.isalnum, s.lower()))
    return s == s[::-1]


def celsius_to_fahrenheit(c: float) -> float:
    """Конвертирует градусы Цельсия в Фаренгейты"""
    return (c * 9 / 5) + 32


def factorial(n: int) -> int:
    """Вычисляет факториал числа"""
    if n < 0:
        raise ValueError("Факториал отрицательного числа"
                         " не определен")
    return 1 if n == 0 else n * factorial(n - 1)


def is_prime(n: int) -> bool:
    """Проверяет является ли число простым"""
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def find_max(numbers: list) -> float:
    """Находит максимальное число в списке"""
    return max(numbers) if numbers else None


def find_min(numbers: list) -> float:
    """Находит минимальное число в списке"""
    return min(numbers) if numbers else None


def count_words(s: str) -> int:
    """Считает количество слов в строке"""
    return len(s.split())


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("Fibonacci is"
                         " not defined for"
                         " negative numbers")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def sum_numbers(numbers: list) -> float:
    return sum(numbers)


if __name__ == "__main__":
    run_dump_server(8000)
