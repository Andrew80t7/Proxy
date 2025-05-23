# main.py

import sys
import time
from Server.ProxyServer import ProxyServer
from Logs.logger import get_logger
from typing import Union

logger = get_logger()
HOST = "localhost"
PORT = 8080


# Добавляем демонстрационные функции -------------------------------------------

def is_palindrome(s: str) -> bool:
    """
    Проверяет, является ли строка палиндромом.

    Аргументы:
        s (str): Входная строка для проверки

    Возвращает:
        bool: True если строка палиндром, иначе False

    Примеры:
        >>> is_palindrome("radar")
        True
        >>> is_palindrome("hello")
        False
    """
    try:
        cleaned = ''.join(filter(str.isalnum, s.lower()))
        return cleaned == cleaned[::-1]
    except (TypeError, AttributeError):
        logger.error("Некорректный тип данных для проверки палиндрома")
        return False


def fibonacci(n: int) -> int:
    """
    Вычисляет n-ное число Фибоначчи.

    Аргументы:
        n (int): Позиция в последовательности (n >= 0)

    Возвращает:
        int: Число Фибоначчи

    Исключения:
        ValueError: Если n < 0
    """
    if n < 0:
        raise ValueError("n не может быть отрицательным")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def celsius_to_fahrenheit(temp: Union[int, float]) -> float:
    """
    Конвертирует градусы Цельсия в Фаренгейты.

    Аргументы:
        temp (int/float): Температура в Цельсиях

    Возвращает:
        float: Температура в Фаренгейтах

    Пример:
        >>> celsius_to_fahrenheit(0)
        32.0
    """
    try:
        return (temp * 9 / 5) + 32
    except TypeError:
        logger.error("Некорректный тип температуры")
        raise


def run_demo_functions():
    """Демонстрация работы простых функций"""
    logger.info("Демонстрация функций:")

    # Проверка палиндрома
    test_str = "A man, a plan, a canal: Panama"
    logger.info(f"'{test_str}' - палиндром? {is_palindrome(test_str)}")

    # Число Фибоначчи
    n = 10
    logger.info(f"Фибоначчи({n}) = {fibonacci(n)}")

    # Конвертация температуры
    temp_c = 25.5
    logger.info(f"{temp_c}°C = {celsius_to_fahrenheit(temp_c)}°F")


# Основная логика прокси ------------------------------------------------------

def run():
    """Запускает ProxyServer и корректно его останавливает."""
    server = None
    try:
        # Запускаем демо-функции перед стартом сервера
        run_demo_functions()

        server = ProxyServer(HOST, PORT)
        logger.info(f"Сервер запущен на {HOST}:{PORT}")
        server.main_loop()
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, остановка сервера")
    except Exception as e:
        logger.error(f"Ошибка при работе сервера: {e}")
        sys.exit(1)
    finally:
        if server:
            server.shutdown()
        time.sleep(1)


if __name__ == "__main__":
    run()