import math
import os
import string
import tempfile
import unittest
from Server.ProxyServer import (ProxyServer,
                                fibonacci,
                                Is_prime,
                                Is_palindrome,
                                Factorial,
                                Reverse_string,
                                AD_HOSTS_1,
                                is_ad_host,
                                modify_html,
                                Time_to_seconds,
                                is_prime_v2,
                                Circle_area,
                                is_pangram,
                                Count_words,
                                Find_max,
                                Is_leap_year,
                                Km_to_miles,
                                sum_list,
                                Is_even,
                                Is_arithmetic_sequence,
                                calculate_kinetic_energy,
                                Caesar_cipher,
                                calculate_variance,
                                sum_digits,
                                kg_to_pounds,
                                triangle_area,
                                is_weekend,
                                rot13,
                                count_consonants,
                                Lcm, square, count_lines,
                                is_perfect_square,
                                filter_even,
                                generate_primes,
                                recursive_factorial,
                                Binary_to_decimal,
                                decimal_to_binary,
                                cube, is_positive,
                                Celsius_to_kelvin,
                                remove_whitespace,

                                get_century,
                                is_strong_password,
                                circle_circumference,
                                minutes_to_hours,
                                flatten_list,
                                remove_duplicates,
                                find_min,
                                is_valid_isbn10,
                                time_to_seconds,
                                count_vowels,
                                caesar_cipher,
                                is_leap_year,
                                calculate_average,
                                circle_area,
                                km_to_miles,
                                reverse_string,
                                is_prime,
                                gcd,
                                generate_password,
                                is_palindrome,
                                celsius_to_fahrenheit,
                                find_max,
                                factorial,
                                is_even, lcm)


class DummySocket:
    def __init__(self):
        self._closed = False

    def fileno(self):
        return -1

    def close(self):
        self._closed = True


class FakeServer:

    def __init__(self):
        pass

    def accept(self):
        raise OSError("fail")

    def settimeout(self, t):
        pass

    def setsockopt(self, *args, **kwargs):
        pass

    def bind(self, *args, **kwargs):
        pass

    def listen(self, *args, **kwargs):
        pass

    def close(self):
        pass

    def fileno(self):
        # чтобы select не включал его
        return -1


class TestHTMLUtils(unittest.TestCase):
    def test_modify_html_removal_and_style(self):
        html = (b"<html><head></head><body>"
                b"<div class='ad-container'>Ad"
                b"</div>"
                b"<p>Hello</p></body></html>")

        cleaned, blocked = modify_html(html)
        text = cleaned.decode('utf-8')
        self.assertNotIn('ad-container', text)
        self.assertIn('<style>', text)
        # blocked should contain one element
        self.assertEqual(len(blocked), 1)
        self.assertEqual(blocked[0]['selector'],
                         '.ad-container')


class TestAdHostUtils(unittest.TestCase):
    def test_is_ad_host(self):
        # clear and set
        AD_HOSTS_1.clear()
        AD_HOSTS_1.update({'ads.test.com'})
        self.assertTrue(
            is_ad_host('ads.test.com'))
        self.assertTrue(
            is_ad_host('sub.ads.test.com'))
        self.assertFalse(
            is_ad_host('example.com'))


class TestProxyServer(unittest.TestCase):

    def test_factorial_positive(self):
        self.assertEqual(
            Factorial(0), 1)
        self.assertEqual(
            Factorial(5), 120)

    def test_factorial_negative(self):
        with self.assertRaises(ValueError):
            Factorial(-3)

    def test_is_palindrome(self):
        self.assertTrue(
            Is_palindrome("A man, a plan, "
                          "a canal: Panama"))
        self.assertFalse(
            Is_palindrome("Hello"))
        self.assertTrue(
            Is_palindrome(""))

    def test_is_prime(self):
        self.assertFalse(Is_prime(0))
        self.assertFalse(Is_prime(1))
        self.assertTrue(Is_prime(2))
        self.assertTrue(Is_prime(13))
        self.assertFalse(Is_prime(15))

    def test_fibonacci_valid(self):
        self.assertEqual(
            fibonacci(0), 0)
        self.assertEqual(
            fibonacci(1), 1)
        self.assertEqual(
            fibonacci(7), 13)

    def test_fibonacci_negative(self):
        with self.assertRaises(ValueError):
            fibonacci(-1)

    def test_reverse_string(self):
        self.assertEqual(Reverse_string("abc"),
                         "cba")
        self.assertEqual(Reverse_string(""),
                         "")

    def setUp(self):
        self.srv = ProxyServer('127.0.0.1',
                               0)

    def tearDown(self):
        self.srv.shutdown()

    def test_init_and_shutdown(self):
        self.assertTrue(self.srv.running)
        self.srv.shutdown()
        self.assertFalse(self.srv.running)

    def test_cleanup_inactive(self):
        dummy = DummySocket()
        self.srv.input_list.append(dummy)
        # форсим необходимость очистки
        self.srv.last_cleanup -= 100
        self.srv._cleanup_inactive_connections()
        self.assertNotIn(dummy, self.srv.input_list)

    def test_on_accept_error(self):
        fake = FakeServer()
        # Заменяем и в input_list
        self.srv.input_list[0] = fake
        self.srv.server = fake
        try:
            self.srv.on_accept()
        except Exception as e:
            self.fail(f"on_accept() "
                      f"не должна выбрасывать,"
                      f" но выбросила: {e}")


class TestNewFunctions(unittest.TestCase):

    def test_is_even(self):
        self.assertTrue(Is_even(0))
        self.assertTrue(Is_even(-4))
        self.assertFalse(Is_even(3))
        self.assertFalse(Is_even(9999999))

    def test_sum_list(self):
        self.assertEqual(sum_list([1, 2, 3]), 6)
        self.assertEqual(sum_list([]), 0)
        self.assertAlmostEqual(sum_list([1.5, 2.5]), 4.0)
        self.assertEqual(sum_list([-10, 5]), -5)

    def test_km_to_miles(self):
        self.assertAlmostEqual(Km_to_miles(1),
                               0.621371)
        self.assertAlmostEqual(Km_to_miles(0),
                               0.0)
        self.assertAlmostEqual(Km_to_miles(100),
                               62.1371)

    def test_is_leap_year(self):
        self.assertTrue(Is_leap_year(2000))
        self.assertTrue(Is_leap_year(2020))
        self.assertFalse(Is_leap_year(1900))
        self.assertFalse(Is_leap_year(2021))
        self.assertTrue(Is_leap_year(2012))

    def test_find_max(self):
        self.assertEqual(Find_max([3, 1, 4, 2]), 4)
        self.assertEqual(Find_max([-5, -1, -10]), -1)
        self.assertIsNone(Find_max([]))
        self.assertEqual(Find_max([5.5, 3.3]), 5.5)

    def test_count_words(self):
        self.assertEqual(Count_words("Hello world"), 2)
        self.assertEqual(Count_words(""), 0)
        self.assertEqual(Count_words("   Multiple   spaces   "),
                         2)
        self.assertEqual(Count_words("No-spaces-here"), 1)

    def test_is_pangram(self):
        self.assertTrue(is_pangram("The quick brown"
                                   " fox jumps over the lazy dog"))
        self.assertFalse(is_pangram("Hello world"))
        self.assertTrue(is_pangram("Pack my box with"
                                   " five dozen liquor jugs"))
        self.assertFalse(is_pangram(""))

    def test_circle_area(self):
        self.assertAlmostEqual(Circle_area(1),
                               3.14159,
                               places=4)
        self.assertAlmostEqual(Circle_area(2.5),
                               19.6349375,
                               places=4)
        with self.assertRaises(ValueError):
            Circle_area(-5)

    def test_time_to_seconds(self):
        self.assertEqual(Time_to_seconds(1, 30),
                         5400)
        self.assertEqual(Time_to_seconds(0, 45),
                         2700)
        self.assertEqual(Time_to_seconds(2, 0),
                         7200)
        with self.assertRaises(ValueError):
            Time_to_seconds(-1, 10)
        with self.assertRaises(ValueError):
            Time_to_seconds(2, -5)

    def test_is_prime_v2(self):
        self.assertTrue(is_prime_v2(2))
        self.assertTrue(is_prime_v2(7919))
        self.assertFalse(is_prime_v2(1))
        self.assertFalse(is_prime_v2(4))
        self.assertFalse(is_prime_v2(-5))


class TestFunctions(unittest.TestCase):
    # Математические функции
    def test_square(self):
        self.assertEqual(square(5),
                         25)
        self.assertEqual(square(-3),
                         9)
        self.assertAlmostEqual(square(2.5),
                               6.25)

    def test_lcm(self):
        self.assertEqual(Lcm(12, 18),
                         36)
        self.assertEqual(Lcm(0, 5),
                         0)
        self.assertEqual(Lcm(7, 3),
                         21)

    # Строковые операции
    def test_count_consonants(self):
        self.assertEqual(count_consonants("Hello World"),
                         7)
        self.assertEqual(count_consonants("AEIOU"),
                         0)

    def test_rot13(self):
        self.assertEqual(rot13("Hello"), "Uryyb")
        self.assertEqual(rot13("Test123"), "Grfg123")

    # Работа с датами
    def test_is_weekend(self):
        self.assertTrue(is_weekend("2023-10-14"))  # Saturday
        self.assertFalse(is_weekend("2023-10-16"))  # Monday

    # Валидация данных
    # Геометрические расчеты
    def test_triangle_area(self):
        self.assertAlmostEqual(triangle_area(4, 5),
                               10.0)
        self.assertAlmostEqual(triangle_area(2.5, 4),
                               5.0)

    # Преобразования
    def test_kg_to_pounds(self):
        self.assertAlmostEqual(kg_to_pounds(1),
                               2.20462, places=4)
        self.assertAlmostEqual(kg_to_pounds(50),
                               110.231, places=2)

    # Рекурсивные функции
    def test_sum_digits(self):
        self.assertEqual(sum_digits(1234),
                         10)
        self.assertEqual(sum_digits(-567),
                         18)

    # Статистика
    def test_calculate_variance(self):
        data = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(calculate_variance(data),
                               2.0)

    # Шифрование
    def test_caesar_cipher(self):
        self.assertEqual(Caesar_cipher("XYZ", 3), "ABC")
        self.assertEqual(Caesar_cipher("abc", -1), "zab")

    # Физические расчеты
    def test_kinetic_energy(self):
        self.assertAlmostEqual(calculate_kinetic_energy(2,
                                                        3),
                               9.0)
        self.assertAlmostEqual(calculate_kinetic_energy(1.5,
                                                        4),
                               12.0)

    # Проверка последовательностей
    def test_is_arithmetic_sequence(self):
        self.assertTrue(Is_arithmetic_sequence([2, 4, 6, 8]))
        self.assertFalse(Is_arithmetic_sequence([1, 3, 7]))


class TestAllFunctions(unittest.TestCase):

    # Математические функции
    def test_square(self):
        self.assertEqual(square(5), 25)
        self.assertEqual(square(-3), 9)
        self.assertAlmostEqual(square(2.5), 6.25)

    def test_cube(self):
        self.assertEqual(cube(3), 27)
        self.assertEqual(cube(-2), -8)
        self.assertAlmostEqual(cube(1.5), 3.375)

    def test_is_positive(self):
        self.assertTrue(is_positive(5))
        self.assertFalse(is_positive(-3))
        self.assertFalse(is_positive(0))

    def test_celsius_to_kelvin(self):
        self.assertAlmostEqual(Celsius_to_kelvin(0),
                               273.15)
        self.assertAlmostEqual(Celsius_to_kelvin(100),
                               373.15)
        self.assertAlmostEqual(Celsius_to_kelvin(-273.15),
                               0)

    def test_lcm(self):
        self.assertEqual(Lcm(12, 18), 36)
        self.assertEqual(Lcm(0, 5), 0)
        self.assertEqual(Lcm(7, 3), 21)

    # Строковые операции
    def test_count_consonants(self):
        self.assertEqual(count_consonants("Hello World"), 7)
        self.assertEqual(count_consonants("AEIOU"), 0)
        self.assertEqual(count_consonants("12345!@#$%"), 0)

    def test_remove_whitespace(self):
        self.assertEqual(remove_whitespace("  Hello\t\nWorld  "),
                         "HelloWorld")
        self.assertEqual(remove_whitespace("NoSpaces"),
                         "NoSpaces")

    def test_rot13(self):
        self.assertEqual(rot13("Hello"), "Uryyb")
        self.assertEqual(rot13("Test123"), "Grfg123")
        self.assertEqual(rot13(rot13("DoubleTest")), "DoubleTest")

    def test_is_weekend(self):
        self.assertTrue(is_weekend("2023-10-14"))  # Saturday
        self.assertFalse(is_weekend("2023-10-16"))  # Monday
        self.assertTrue(is_weekend("2024-01-07"))  # Sunday

    def test_get_century(self):
        self.assertEqual(get_century(2023), 21)
        self.assertEqual(get_century(1900), 19)
        self.assertEqual(get_century(2000), 20)

    # Валидация данных

    def test_is_strong_password(self):
        self.assertTrue(is_strong_password("Passw0rd!"))
        self.assertFalse(is_strong_password("weak"))
        self.assertFalse(is_strong_password("MissingSpecial1"))

    # Геометрические расчеты
    def test_triangle_area(self):
        self.assertAlmostEqual(triangle_area(4, 5), 10.0)
        self.assertAlmostEqual(triangle_area(2.5, 4), 5.0)

    def test_circle_circumference(self):
        self.assertAlmostEqual(circle_circumference(1),
                               2 * math.pi)
        self.assertAlmostEqual(circle_circumference(2.5),
                               5 * math.pi)

    # Преобразования
    def test_minutes_to_hours(self):
        self.assertAlmostEqual(minutes_to_hours(90), 1.5)
        self.assertAlmostEqual(minutes_to_hours(0), 0.0)

    def test_kg_to_pounds(self):
        self.assertAlmostEqual(kg_to_pounds(1), 2.20462, places=4)
        self.assertAlmostEqual(kg_to_pounds(50), 110.231, places=2)

    # Работа со списками
    def test_flatten_list(self):
        self.assertEqual(flatten_list([[1, 2], [3], [4, 5]]),
                         [1, 2, 3, 4, 5])
        self.assertEqual(flatten_list([]), [])

    def test_remove_duplicates(self):
        self.assertEqual(remove_duplicates([1, 2, 2, 3, 3, 3]), [1, 2, 3])
        self.assertEqual(remove_duplicates(["a", "b", "a"]), ["a", "b"])

    # Бинарные операции
    def test_decimal_to_binary(self):
        self.assertEqual(decimal_to_binary(5), "101")
        self.assertEqual(decimal_to_binary(0), "0")

    def test_binary_to_decimal(self):
        self.assertEqual(Binary_to_decimal("101"), 5)
        self.assertEqual(Binary_to_decimal("0"), 0)

    # Рекурсивные функции
    def test_sum_digits(self):
        self.assertEqual(sum_digits(1234),
                         10)
        self.assertEqual(sum_digits(-567),
                         18)
        self.assertEqual(sum_digits(0),
                         0)

    def test_recursive_factorial(self):
        self.assertEqual(recursive_factorial(5),
                         120)
        self.assertEqual(recursive_factorial(0),
                         1)

    # Генераторы данных
    def test_generate_primes(self):
        self.assertEqual(generate_primes(10),
                         [2, 3, 5, 7])
        self.assertEqual(generate_primes(2),
                         [2])

    # Статистика
    def test_calculate_variance(self):
        data = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(calculate_variance(data),
                               2.0)
        self.assertAlmostEqual(calculate_variance([5]),
                               0.0)

    # Фильтрация
    def test_filter_even(self):
        self.assertEqual(filter_even([1, 2, 3, 4, 5]),
                         [2, 4])
        self.assertEqual(filter_even([]), [])

    # Валидация чисел
    def test_is_perfect_square(self):
        self.assertTrue(is_perfect_square(25))
        self.assertFalse(is_perfect_square(26))
        self.assertTrue(is_perfect_square(0))

    # Шифрование
    def test_caesar_cipher(self):
        self.assertEqual(Caesar_cipher("XYZ", 3), "ABC")
        self.assertEqual(Caesar_cipher("abc", -1), "zab")
        self.assertEqual(Caesar_cipher("Hello!", 13), "Uryyb!")

    # Физические расчеты
    def test_calculate_kinetic_energy(self):
        self.assertAlmostEqual(calculate_kinetic_energy(2,
                                                        3),
                               9.0)
        self.assertAlmostEqual(calculate_kinetic_energy(1.5,
                                                        4),
                               12.0)

    # Проверка последовательностей
    def test_is_arithmetic_sequence(self):
        self.assertTrue(Is_arithmetic_sequence([2, 4, 6, 8]))
        self.assertFalse(Is_arithmetic_sequence([1, 3, 7]))
        self.assertTrue(Is_arithmetic_sequence([]))
        self.assertTrue(Is_arithmetic_sequence([5]))

    # Работа с файлами
    def test_count_lines(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Line1\nLine2\nLine3")
            f.close()
            self.assertEqual(count_lines(f.name), 3)
            os.unlink(f.name)


class Test_do_AllFunctions(unittest.TestCase):

    # 1. Проверка четности числа
    def test_is_even(self):
        self.assertTrue(is_even(4))
        self.assertFalse(is_even(5))
        self.assertTrue(is_even(0))

    # 2. Расчет факториала
    def test_factorial(self):
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(0), 1)
        with self.assertRaises(ValueError):
            factorial(-1)

    # 3. Поиск максимального числа
    def test_find_max(self):
        self.assertEqual(find_max([3, 1, 4, 2]), 4)
        self.assertIsNone(find_max([]))
        self.assertEqual(find_max([-5, -1, -10]), -1)

    # 4. Конвертация Celsius в Fahrenheit
    def test_celsius_to_fahrenheit(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32.0)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212.0)

    # 5. Проверка палиндрома
    def test_is_palindrome(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))
        self.assertFalse(is_palindrome("Hello World"))

    # 6. Генерация случайного пароля
    def test_generate_password(self):
        password = generate_password(12)
        self.assertEqual(len(password), 12)
        self.assertTrue(any(c in string.ascii_letters for c in password))

    # 7. Расчет НОД
    def test_gcd(self):
        self.assertEqual(gcd(54, 24), 6)
        self.assertEqual(gcd(0, 5), 5)

    # 8. Проверка простого числа
    def test_is_prime(self):
        self.assertTrue(is_prime(7919))
        self.assertFalse(is_prime(1))
        self.assertFalse(is_prime(4))

    # 9. Реверс строки
    def test_reverse_string(self):
        self.assertEqual(reverse_string("hello"), "olleh")
        self.assertEqual(reverse_string(""), "")

    # 10. Конвертация километров в мили
    def test_km_to_miles(self):
        self.assertAlmostEqual(km_to_miles(1), 0.621371)
        self.assertAlmostEqual(km_to_miles(0), 0.0)

    # 11. Расчет площади круга
    def test_circle_area(self):
        self.assertAlmostEqual(circle_area(2), math.pi * 4)
        with self.assertRaises(ValueError):
            circle_area(-1)

    # 12. Поиск среднего значения
    def test_calculate_average(self):
        self.assertEqual(calculate_average([1, 2, 3, 4, 5]),
                         3.0)
        with self.assertRaises(ValueError):
            calculate_average([])

    # 13. Проверка високосного года
    def test_is_leap_year(self):
        self.assertTrue(is_leap_year(2000))
        self.assertFalse(is_leap_year(1900))
        self.assertTrue(is_leap_year(2020))

    # 14. Шифр Цезаря
    def test_caesar_cipher(self):
        self.assertEqual(caesar_cipher("XYZ", 3),
                         "ABC")
        self.assertEqual(caesar_cipher("abc", -1),
                         "zab")

    # 15. Подсчет гласных
    def test_count_vowels(self):
        self.assertEqual(count_vowels("Hello World"), 3)
        self.assertEqual(count_vowels("Привет"), 2)

    # 16. Конвертация времени в секунды
    def test_time_to_seconds(self):
        self.assertEqual(time_to_seconds(1, 30, 15), 5415)
        self.assertEqual(time_to_seconds(0, 0, 0), 0)

    # 17. Проверка ISBN-10
    def test_is_valid_isbn10(self):
        self.assertTrue(is_valid_isbn10("0-306-40615-2"))
        self.assertFalse(is_valid_isbn10("1234567890"))

    # 18. Поиск минимального числа
    def test_find_min(self):
        self.assertEqual(find_min([3, 1, 4, 2]), 1)
        self.assertIsNone(find_min([]))

    # 19. Расчет НОК
    def test_lcm(self):
        self.assertEqual(lcm(12, 18), 36)
        self.assertEqual(lcm(0, 5), 0)


if __name__ == "__main__":
    unittest.main()
