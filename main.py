# main.py
import math
import sys
import time
from Server.ProxyServer import ProxyServer
from Logs.logger import get_logger
from typing import Union, List

logger = get_logger()
HOST = "localhost"
PORT = 8080


def is_prime(n: int) -> bool:
    """Проверяет, является ли число простым"""
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def reverse_string(s: str) -> str:
    """Возвращает обратную строку"""
    return s[::-1]


def count_vowels(s: str) -> int:
    """Считает количество гласных букв в строке"""
    vowels = 'aeiouаеёиоуыэюя'
    return sum(1 for char in s.lower() if char in vowels)


def meters_to_feet(m: Union[int, float]) -> float:
    """Конвертирует метры в футы"""
    try:
        return m * 3.28084
    except TypeError:
        logger.error("Некорректный тип данных"
                     " для конвертации метров в футы")
        raise


def gcd(a: int, b: int) -> int:
    """Находит наибольший общий делитель двух чисел"""
    while b:
        a, b = b, a % b
    return a


def is_anagram(s1: str, s2: str) -> bool:
    """Проверяет, являются ли строки анаграммами"""
    return sorted(
        s1.lower().
        replace(" ", "")) == sorted(s2.lower().
                                    replace(" ", ""))


def average(nums: List[Union[int, float]]) -> float:
    """Вычисляет среднее значение списка чисел"""
    if not nums:
        raise ValueError("Список чисел не может быть пустым")
    return sum(nums) / len(nums)


# Добавляем демонстрационные функции

def is_palindrome(s: str) -> bool:
    try:
        cleaned = ''.join(filter(str.isalnum, s.lower()))
        return cleaned == cleaned[::-1]
    except (TypeError, AttributeError):
        logger.error("Некорректный тип "
                     "данных для проверки палиндрома")
        return False


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n не может"
                         " быть отрицательным")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def celsius_to_fahrenheit(temp: Union[int, float]) -> float:
    try:
        return (temp * 9 / 5) + 32
    except TypeError:
        logger.error("Некорректный"
                     " тип температуры")
        raise


def run_demo_functions():
    logger.info("Демонстрация функций:")

    # Проверка палиндрома
    test_str = "A man, a plan, a canal: Panama"
    logger.info(f"'{test_str}' -"
                f" палиндром? {is_palindrome(test_str)}")

    # Число Фибоначчи
    n = 10
    logger.info(f"Фибоначчи({n}) = {fibonacci(n)}")

    # Конвертация температуры
    temp_c = 25.5
    logger.info(f"{temp_c}°C ="
                f" {celsius_to_fahrenheit(temp_c)}°F")


# Основная логик

def run():
    server = None
    try:
        run_demo_functions()

        server = ProxyServer(HOST, PORT)
        logger.info(f"Сервер запущен"
                    f" на {HOST}:{PORT}")
        server.main_loop()
    except KeyboardInterrupt:
        logger.info("Получен сигнал"
                    " прерывания, остановка"
                    " сервера")
    except Exception as e:
        logger.error(f"Ошибка при работе"
                     f" сервера: {e}")
        sys.exit(1)
    finally:
        if server:
            server.shutdown()
        time.sleep(1)


if __name__ == "__main__":
    run()
    print('\n')
