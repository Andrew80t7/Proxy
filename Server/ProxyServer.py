import math
import random
import socket
import string
import time
from datetime import datetime

import select
import errno
import os
from Connection.Forward import Forward
from Logs.logger import get_logger
from typing import Tuple, List, Union, Optional
import re
from bs4 import BeautifulSoup

DUMP_DIR = os.path.join(os.path.dirname(__file__), "dumps")
os.makedirs(DUMP_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(__file__)
AD_HOSTS_PATH = os.path.join(BASE_DIR, "ad_hosts.txt")

AD_HOSTS_1 = set()

logger = get_logger()


def is_even(n: int) -> bool:
    return n % 2 == 0


# 2. Расчет факториала
def factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Факториал отрицательного числа не определен")
    return 1 if n == 0 else n * Factorial(n - 1)


# 3. Поиск максимального числа в списке
def find_max(numbers: List[Union[int, float]]) -> Optional[Union[int, float]]:
    return max(numbers) if numbers else None


# 4. Конвертация Celsius в Fahrenheit
def celsius_to_fahrenheit(c: float) -> float:
    return (c * 9 / 5) + 32


# 5. Проверка палиндрома
def is_palindrome(s: str) -> bool:
    s = re.sub(r'[^A-Za-z0-9]', '', s.lower())
    return s == s[::-1]


# 6. Генерация случайного пароля
def generate_password(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))


# 7. Расчет НОД
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


# 8. Проверка простого числа
def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


# 9. Реверс строки
def reverse_string(s: str) -> str:
    return s[::-1]


# 10. Конвертация километров в мили
def km_to_miles(km: float) -> float:
    return km * 0.621371


# 11. Расчет площади круга
def circle_area(radius: float) -> float:
    if radius < 0:
        raise ValueError("Радиус не может быть отрицательным")
    return math.pi * radius ** 2


# 12. Поиск среднего значения
def calculate_average(numbers: List[float]) -> float:
    if not numbers:
        raise ValueError("Список чисел не может быть пустым")
    return sum(numbers) / len(numbers)


# 13. Проверка високосного года
def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


# 14. Шифр Цезаря
def caesar_cipher(text: str, shift: int) -> str:
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            result.append(char)
    return ''.join(result)


# 15. Подсчет гласных в строке
def count_vowels(s: str) -> int:
    vowels = 'aeiouAEIOUаеёиоуыэюяАЕЁИОУЫЭЮЯ'
    return sum(1 for char in s if char in vowels)


# 16. Конвертация времени в секунды
def time_to_seconds(hours: int, minutes: int, seconds: int) -> int:
    return hours * 3600 + minutes * 60 + seconds


# 17. Проверка ISBN-10
def is_valid_isbn10(isbn: str) -> bool:
    isbn = isbn.replace('-', '')
    if len(isbn) != 10:
        return False
    total = 0
    for i, c in enumerate(isbn):
        if c == 'X' and i == 9:
            total += 10 * (10 - i)
        elif not c.isdigit():
            return False
        else:
            total += int(c) * (10 - i)
    return total % 11 == 0


# 18. Поиск минимального числа
def find_min(numbers: List[Union[int, float]]) -> Optional[Union[int, float]]:
    return min(numbers) if numbers else None


# 19. Расчет НОК
def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


# 20. Генерация последовательности Фибоначчи
def fibonacci_sequence(n: int) -> List[int]:
    if n <= 0:
        return []
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]


# 21. Проверка анаграммы
def is_anagram(s1: str, s2: str) -> bool:
    s1 = re.sub(r'[^A-Za-z0-9]', '', s1.lower())
    s2 = re.sub(r'[^A-Za-z0-9]', '', s2.lower())
    return sorted(s1) == sorted(s2)


# 22. Конвертация римских чисел в арабские
def roman_to_int(roman: str) -> int:
    roman_numerals = {'I': 1,
                      'V': 5,
                      'X': 10,
                      'L': 50,
                      'C': 100,
                      'D': 500,
                      'M': 1000}
    total = 0
    prev_value = 0
    for char in reversed(roman):
        value = roman_numerals[char]
        total += value if value >= prev_value else -value
        prev_value = value
    return total


# 23. Расчет BMI
def calculate_bmi(weight: float, height: float) -> float:
    if height <= 0:
        raise ValueError("Рост должен быть положительным числом")
    return weight / (height ** 2)


# 24. Поиск уникальных элементов
def unique_elements(lst: List) -> List:
    return list(set(lst))


# 25. Проверка совершенного числа
def is_perfect_number(n: int) -> bool:
    if n <= 0:
        return False
    divisors_sum = sum(i for i in range(1, n) if n % i == 0)
    return divisors_sum == n


# 26. Генерация случайного RGB-цвета
def random_rgb_color() -> tuple:
    return (random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))

    # 27. Подсчет слов в строке


def count_words(text: str) -> int:
    return len(text.split())


# 28. Проверка мощности двойки
def is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def degrees_to_radians(degrees: float) -> float:
    return degrees * math.pi / 180


# 30. Расчет расстояния между точками
def distance_between_points(x1: float,
                            y1: float,
                            x2: float,
                            y2: float) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# 31. Поиск медианы списка
def find_median(numbers: List[float]) -> float:
    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)
    if n == 0:
        raise ValueError("Список чисел не может быть пустым")
    mid = n // 2
    return ((sorted_numbers[mid] + sorted_numbers[-mid - 1]) /
            2) if n % 2 == 0 else sorted_numbers[mid]


# 32. Проверка валидности email
def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


# 33. Расчет аннуитетного платежа
def annuity_payment(principal: float,
                    rate: float,
                    periods: int) -> float:
    monthly_rate = rate / 12 / 100
    return (principal * (monthly_rate * (1 + monthly_rate) ** periods) /
            ((1 + monthly_rate) ** periods - 1))


# 34. Поиск наиболее частого элемента
def most_frequent_element(lst: List) -> any:
    return max(set(lst), key=lst.count) if lst else None


# 35. Генерация таблицы умножения
def multiplication_table(n: int) -> List[List[int]]:
    return [[i * j for j in range(1, n + 1)] for i in range(1, n + 1)]


# 36. Проверка сбалансированных скобок
def is_balanced_brackets(s: str) -> bool:
    stack = []
    brackets = {'(': ')', '[': ']', '{': '}'}
    for char in s:
        if char in brackets:
            stack.append(char)
        elif char in brackets.values():
            if not stack or brackets[stack.pop()] != char:
                return False
    return not stack


# 37. Расчет суммы цифр числа
def sum_of_digits(n: int) -> int:
    return sum(int(digit) for digit in str(abs(n)))


# 38. Конвертация секунд в время
def seconds_to_time(seconds: int) -> tuple:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return (hours, minutes, secs)


# 39. Поиск пересечения списков
def list_intersection(a: List, b: List) -> List:
    return list(set(a) & set(b))


# 40. Проверка треугольника
def is_valid_triangle(a: float, b: float, c: float) -> bool:
    return a + b > c and a + c > b and b + c > a


# 41. Расчет площади прямоугольника
def rectangle_area(length: float, width: float) -> float:
    if length <= 0 or width <= 0:
        raise ValueError("Длина и ширина должны быть положительными")
    return length * width


# 42. Генерация случайной строки
def random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits,
                                  k=length))


# 43. Проверка армстронгового числа
def is_armstrong_number(n: int) -> bool:
    digits = [int(d) for d in str(n)]
    num_digits = len(digits)
    return n == sum(d ** num_digits for d in digits)


# 44. Конвертация температуры в Кельвины
def celsius_to_kelvin(c: float) -> float:
    return c + 273.15


# 45. Поиск глубины списка
def list_depth(lst: List) -> int:
    if isinstance(lst, list):
        return 1 + max((list_depth(item) for item in lst),
                       default=0)
    return 0


# 46. Расчет площади треугольника по формуле Герона
def heron_triangle_area(a: float, b: float, c: float) -> float:
    if not is_valid_triangle(a, b, c):
        raise ValueError("Недопустимые стороны треугольника")
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


# 47. Проверка последовательности
def is_arithmetic_sequence(sequence: List[Union[int, float]]) -> bool:
    if len(sequence) < 2:
        return True
    diff = sequence[1] - sequence[0]
    return all(sequence[i + 1] -
               sequence[i] ==
               diff for i in range(len(sequence) - 1))


# 48. Поиск наибольшего общего делителя трех чисел
def gcd_three(a: int, b: int, c: int) -> int:
    return gcd(gcd(a, b), c)


# 49. Конвертация двоичного числа в десятичное
def binary_to_decimal(binary: str) -> int:
    return int(binary, 2)


# 50. Проверка номера кредитной карты (алгоритм Луна)
def is_valid_credit_card(card_number: str) -> bool:
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            doubled = digit * 2
            checksum += doubled // 10 + doubled % 10
        else:
            checksum += digit
    return checksum % 10 == 0


def square(n: Union[int, float]) -> Union[int, float]:
    return n ** 2


def cube(n: Union[int, float]) -> Union[int, float]:
    return n ** 3


def is_positive(n: Union[int, float]) -> bool:
    return n > 0


def Celsius_to_kelvin(temp: float) -> float:
    return temp + 273.15


def Lcm(a: int, b: int) -> int:
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
def Is_valid_email(email: str) -> bool:
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


def Binary_to_decimal(binary: str) -> int:
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
            sieve[i * i: n + 1: i] = \
                [False] * len(sieve[i * i: n + 1: i])
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
def Caesar_cipher(text: str, shift: int) -> str:
    results = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            results.append(chr((ord(char) -
                                base + shift) % 26 + base))
        else:
            results.append(char)
    return ''.join(results)


# Физические расчеты
def calculate_kinetic_energy(mass: float, velocity: float) -> float:
    return 0.5 * mass * velocity ** 2


# Проверка последовательностей
def Is_arithmetic_sequence(sequence: List[Union[int, float]]) -> bool:
    if len(sequence) < 2:
        return True
    diff = sequence[1] - sequence[0]
    return all(sequence[i + 1] -
               sequence[i] == diff for i in range(len(sequence) - 1))


# Работа с файлами
def count_lines(filename: str) -> int:
    with open(filename, 'r') as file:
        return sum(1 for _ in file)


def Is_even(n: int) -> bool:
    """Проверяет чётность числа"""
    return n % 2 == 0


def sum_list(numbers: list) -> float:
    """Возвращает сумму элементов списка"""
    return sum(numbers)


def Km_to_miles(km: float) -> float:
    """Конвертирует километры в мили"""
    return km * 0.621371


def Is_leap_year(year: int) -> bool:
    """Проверяет високосный год"""
    if year % 4 != 0:
        return False
    elif year % 100 != 0:
        return True
    elif year % 400 == 0:
        return True
    else:
        return False


def Find_max(numbers: list) -> float:
    """Находит максимальное число в списке"""
    return max(numbers) if numbers else None


def Count_words(text: str) -> int:
    """Считает количество слов в строке"""
    return len(text.split())


def is_pangram(s: str) -> bool:
    """Проверяет панграмму (содержит все буквы алфавита)"""
    alphabet = set('abcdefghijklmnopqrstuvwxyz')
    return alphabet.issubset(s.lower())


def Circle_area(radius: float) -> float:
    """Вычисляет площадь круга"""
    if radius < 0:
        raise ValueError("Радиус не может быть отрицательным")
    return 3.14159 * radius ** 2


def Time_to_seconds(hours: int, minutes: int) -> int:
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


def Factorial(n: int) -> int:
    if n < 0:
        raise ValueError("Negative input not allowed")
    return 1 if n == 0 else n * Factorial(n - 1)


def Is_palindrome(s: str) -> bool:
    import re
    cleaned = re.sub(r'[^A-Za-z0-9]',
                     '', s).lower()
    return cleaned == cleaned[::-1]


def Is_prime(n: int) -> bool:
    """Check if n is a prime number."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number."""
    if n < 0:
        raise ValueError("Negative index not allowed")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def Reverse_string(s: str) -> str:
    """Return the reverse of the string s."""
    return s[::-1]


def modify_html(html: bytes) -> Tuple[bytes, List[dict]]:
    """
    удаляет рекламу
    """
    blocked_elements = []
    try:
        soup = BeautifulSoup(html, "html.parser")

        ad_selectors = [
            "div[data-ad-target]",
            ".ad-container",
            ".ad-wrapper",
            'div[id^="adfox_"]',
            'iframe[src*="ads."]',
            'div[class*="banner_ad"]',
            'div[data-type="adsContainer"]',
            'script[src*="adservice"]',
            'img[src*="ads."]',
        ]
        for selector in ad_selectors:
            for tag in soup.select(selector):
                blocked_elements.append(
                    {
                        "selector": selector,
                        "src": tag.get("src", ""),
                        "classes": tag.get("class", ""),
                        "tag": tag.name,
                    }
                )
                tag.decompose()

        style = soup.new_tag("style")
        style.string = """
            .telegram-banner, .casino-banner, .shopping-banner {
                position: fixed !important;
                bottom: 20px !important;
                right: 20px !important;
                z-index: 9999 !important;
                visibility: visible !important;
            }
        """
        if soup.head:
            soup.head.append(style)
        else:
            soup.insert(0, style)

        return str(soup).encode("utf-8"), blocked_elements

    except Exception:
        pass
        return html, blocked_elements


with open("ad_hosts.txt", "r") as f:
    for line in f:
        host = line.strip()
        if host and not host.startswith("#"):
            AD_HOSTS_1.add(host)


def is_ad_host(hst: str) -> bool:
    """Проверка, является ли домен рекламным"""
    return any(hst == d or hst.endswith("." + d) for d in AD_HOSTS_1)


def save_dump(data: bytes, direction: str):
    """
    Сохраняет данные data в файл:

    """

    ts = datetime.now().isoformat(timespec="microseconds").replace(":",
                                                                   "")
    filename = f"{ts}_{direction}.dump"
    path = os.path.join(DUMP_DIR, filename)

    with open(path, "wb") as file:
        header = f"Timestamp: {ts}\nDirection: {direction}\n\n"
        file.write(header.encode("utf-8",
                                 errors="ignore"))
        file.write(data)

    logger.debug(f"Dump сохранён: {path}")


# Размер буфера
BUFFER_SIZE = 4096

# Задержка
DELAY = 0.0001

# Таймаут для операций с сокетами
SOCKET_TIMEOUT = 5

# Максимальное количество соединений
MAX_CONNECTIONS = 1000

# логгер
logger = get_logger()


def modify_request(data: bytes) -> bytes:
    try:
        lines = data.split(b"\r\n")
        if not lines:
            return data

        # первая строка: метод, URL, протокол
        first = lines[0].decode("utf-8",
                                errors="ignore").split(" ")
        if len(first) < 3:
            return data
        method, url, proto = first

        if url.startswith("http://") or url.startswith("https://"):
            idx = url.find("/", url.find("://") + 3)
            path = url[idx:] if idx != -1 else "/"
            lines[0] = b" ".join(
                [method.encode(), path.encode(), proto.encode()]
            )
        return b"\r\n".join(lines)
    except UnicodeError:
        pass
        return data


def parse_request(data: bytes):
    """Извлекает метод, хост и порт"""

    lines = data.split(b"\r\n")
    if not lines:
        return None, None, None

    first_line = lines[0].decode("utf-8",
                                 errors="ignore")
    parts = first_line.split(" ")
    if len(parts) < 2:
        return None, None, None

    method = parts[0]

    if method == "CONNECT":
        host_port = parts[1].split(":")
        HOST = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 443
        return "CONNECT", HOST, port
    else:
        # Обработка заголовков
        for tag_line in lines[1:]:
            try:
                line_str = tag_line.decode("utf-8",
                                           errors="ignore")
                if line_str.lower().startswith("host:"):
                    host_port = line_str.split(":",
                                               1)[1].strip()
                    if ":" in host_port:
                        HOST, port = host_port.split(":")
                        port = int(port)
                    else:
                        HOST = host_port
                        port = 80
                    return method, HOST, port
            except Exception:
                pass
        return None, None, None


class ProxyServer:
    """
    Основной класс сервера

    """

    def __init__(self, HOST: str, PORT: int):
        """
        Инициализирует прокси-сервер.

        """
        self.server = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET,
                               socket.SO_REUSEADDR, 1)
        self.server.settimeout(SOCKET_TIMEOUT)
        self.server.setsockopt(socket.IPPROTO_TCP,
                               socket.TCP_NODELAY, 1)
        self.server.bind((HOST, PORT))
        self.server.listen(200)
        self.input_list = [self.server]
        self.channel = {}
        self.running = True
        self.last_cleanup = time.time()
        logger.info(f"Прокси-сервер инициализирован на"
                    f" {HOST}:{PORT}")

    def _cleanup_inactive_connections(self):
        """
        Очищает неактивные соединения
        """

        current_time = time.time()
        if current_time - self.last_cleanup < 60:
            return

        try:

            valid_sockets = []

            for s in self.input_list:
                try:
                    if s.fileno() != -1:
                        valid_sockets.append(s)
                    else:
                        if s in self.channel:
                            self._cleanup_peer_connection(s)
                except OSError:
                    if s in self.channel:
                        self._cleanup_peer_connection(s)

            self.input_list = valid_sockets
            self.last_cleanup = current_time
            logger.info(f"Очищено {len(self.input_list)}"
                        f" активных соединений")
        except OSError as e:
            logger.error(f"Ошибка при очистке соединений:"
                         f" {e}")

    def main_loop(self):
        """
        Основной цикл обработки событий сервера.
        """
        logger.info("Сервер запущен и ожидает"
                    " подключений")

        while self.running:
            try:
                time.sleep(DELAY)
                self._cleanup_inactive_connections()

                if not self.input_list:
                    logger.warning("Нет активных сокетов,"
                                   " завершение работы")
                    break

                input_ready, _, _ = select.select(self.input_list,
                                                  [],
                                                  [],
                                                  0.1)
                for s in input_ready:
                    if s == self.server:
                        self.on_accept()
                    else:
                        self.on_recv(s)
            except select.error as e:
                if e.args[0] == errno.EBADF:
                    logger.warning(
                        "Обнаружен"
                        " невалидный файловый дескриптор,"
                        " очистка сокетов"
                    )
                    self._cleanup_inactive_connections()
                else:
                    logger.error(f"Ошибка select: {e}")
            except Exception as e:
                logger.error(f"Ошибка в главном цикле: {e}")
                self._cleanup_inactive_connections()

    def on_accept(self):
        """
        Обрабатывает новое клиентское подключение.
        """
        try:
            clientsock, clientaddr = self.server.accept()
            clientsock.settimeout(SOCKET_TIMEOUT)
            clientsock.setsockopt(socket.IPPROTO_TCP,
                                  socket.TCP_NODELAY,
                                  1)
            logger.info(f"Новое подключение от"
                        f" {clientaddr}")
            self.input_list.append(clientsock)
            self.channel[clientsock] = {
                "peer": None,
                "parse": True,
                "type": None,
            }
        except socket.timeout:
            pass
        except OSError as e:
            logger.error(f"Ошибка при принятии"
                         f" соединения: {e}")

    def on_recv(self, s: socket.socket):
        """
        Обрабатывает данные от клиента или сервера.
        """
        try:
            # Проверяем, что сокет всё ещё валиден
            if s.fileno() == -1:
                logger.warning("Получен запрос"
                               " от невалидного сокета")
                self._cleanup_inactive_connections()
                return

            data = s.recv(BUFFER_SIZE)
            if not data:
                self.on_close(s)
                return

            # Сохраняем запросы в дампс

            save_dump(data, "request")

            if s in self.channel and self.channel[s]["parse"]:
                method, HOST, port = parse_request(data)

                if method == "CONNECT" and HOST and is_ad_host(HOST):
                    logger.info(f"BLOCKING"
                                f" CONNECT to ad host: {HOST}")
                    s.send(b"HTTP/1.1"
                           b" 403 Forbidden\r\n\r\n")
                    return

                if HOST and is_ad_host(HOST):

                    self.channel[s].setdefault("blocked_count", 0)
                    self.channel[s]["blocked_count"] += 1

                    logger.info(
                        f"Блокировка запроса"
                        f" к рекламному домену: {HOST} "
                        f"(total blocked:"
                        f" {self.channel[s]['blocked_count']})"
                    )
                    if method == "CONNECT":
                        # Блокируем HTTPS CONNECT
                        s.send(b"HTTP/1.1"
                               b" 403 Forbidden\r\n\r\n")
                    else:
                        # Блокируем HTTP-запрос
                        resp = (b"HTTP/1.1"
                                b" 204 No Content\r\nContent-Length:"
                                b" 0\r\n\r\n")
                        s.send(resp)
                        save_dump(resp, "blocked")
                    return

                if method and HOST and port:
                    logger.debug(f"Запрос: {method} {HOST}:{port}")
                    forward = Forward().start(HOST, port)
                    if forward:
                        self._setup_forward_connection(
                            s, forward, method, data
                        )
                    else:
                        self._handle_connection_error(HOST, port, s)
                else:
                    self._handle_invalid_request(s)

            else:
                # Далее передаем данные (HTTP или HTTPS-туннель)
                self._forward_data(s, data)

        except socket.timeout:
            # Игнорируем таймауты при чтении данных
            pass
        except ConnectionAbortedError:
            logger.warning(f"Соединение разорвано: {s.getpeername()}")
            self.on_close(s)
        except OSError as e:
            logger.error(f"Ошибка при получении данных: {e}")
            self.on_close(s)

    def _setup_forward_connection(
            self,
            s: socket.socket,
            forward: socket.socket,
            method: str,
            data: bytes,
    ):
        """
        Настраивает соединение с целевым сервером.
        """
        try:
            self.channel[s]["peer"] = forward
            self.channel[forward] = {"peer": s,
                                     "parse": False,
                                     "type": method}

            if method == "CONNECT":
                self._handle_https_connection(s)
            else:
                self._handle_http_connection(s, forward, data)
        except OSError as e:
            logger.error(f"Ошибка при настройке соединения: {e}")
            self.on_close(s)

    def _handle_https_connection(self, s: socket.socket):
        """
        Обрабатывает HTTPS-соединение
        """
        try:
            logger.debug("Установка HTTPS-соединения")
            # Отправляем успешный ответ клиенту
            s.send(b"HTTP/1.1 200"
                   b" Connection"
                   b" Established\r\n\r\n")

            # Настраиваем соединение
            self.channel[s]["type"] = "CONNECT"
            self.channel[s]["parse"] = False

            # Добавляем peer в список для мониторинга
            peer = self.channel[s]["peer"]
            if peer and peer not in self.input_list:
                self.input_list.append(peer)
                logger.debug("Peer добавлен"
                             " в список мониторинга")

            logger.info("HTTPS-соединение установлено")
        except OSError as e:
            logger.error(f"Ошибка при установке"
                         f" HTTPS-соединения: {e}")
            self.on_close(s)

    def _handle_http_connection(
            self, s: socket.socket,
            forward: socket.socket,
            data: bytes
    ):
        """
        Обрабатывает HTTP-соединение.
        """
        try:
            logger.debug("Обработка HTTP-соединения")
            new_data = modify_request(data)
            forward.send(new_data)
            self.channel[s]["type"] = "HTTP"
            self.channel[s]["parse"] = False
            self.input_list.append(forward)
        except OSError as e:
            logger.error(f"Ошибка при обработке"
                         f" HTTP-соединения: {e}")
            self.on_close(s)

    def _handle_connection_error(self, HOST: str, PORT: int, s: socket.socket):
        """
        Обрабатывает ошибку подключения.
        """
        logger.error(f"Не удалось подключиться к {HOST}:{PORT}")
        self.on_close(s)

    def _handle_invalid_request(self, s: socket.socket):
        """
        Обрабатывает некорректный запрос.
        """
        logger.warning("Получен некорректный запрос")
        self.on_close(s)

    def _forward_data(self, s: socket.socket, data: bytes):
        peer = self.channel[s]["peer"]
        # buf = self.channel[s].sedtdefault('resp_bu')
        save_dump(data, "response")

        if self.channel[s].get("type") != "HTTP":
            peer.send(data)
            return

        buf = self.channel[s].setdefault("resp_buf", b"") + data
        if b"\r\n\r\n" not in buf:
            self.channel[s]["resp_buf"] = buf
            return

        headers, body = buf.split(b"\r\n\r\n", 1)
        headers_str = headers.decode("utf-8", errors="ignore").lower()
        is_html = "content-type:" in headers_str and "text/html" in headers_str

        logger.debug(
            f"is_html={is_html}, headers snippet: {headers_str[:100]!r}"
        )

    def on_close(self, s: socket.socket):
        """
        Закрывает соединение и освобождает ресурсы.

        """
        try:
            if s in self.input_list:
                try:
                    client_addr = s.getpeername()
                    logger.info(f"Закрытие соединения с {client_addr}")
                except OSError:
                    logger.info("Закрытие соединения"
                                " с неизвестным адресом")

                self.input_list.remove(s)
                if s in self.channel:
                    self._cleanup_peer_connection(s)

                try:
                    s.close()
                except OSError:
                    pass
        except OSError as e:
            logger.error(f"Ошибка при закрытии соединения: {e}")

    def _cleanup_peer_connection(self, s: socket.socket):
        """
        Очищает связанные соединения.
        """
        try:
            if s in self.channel:
                peer = self.channel[s]["peer"]
                if peer and peer in self.input_list:
                    self.input_list.remove(peer)
                    try:
                        peer.close()
                    except OSError:
                        pass
                del self.channel[s]
                if peer in self.channel:
                    del self.channel[peer]
        except OSError as e:
            logger.error(f"Ошибка при очистке соединения: {e}")

    def shutdown(self):
        """
        завершает работу сервера.
        """
        logger.info("Завершение работы сервера")
        self.running = False

        for s in list(self.input_list):
            try:
                if s != self.server:
                    self.on_close(s)
            except OSError:
                pass

        try:
            self.server.close()
        except OSError:
            pass

        logger.info("Сервер остановлен")
