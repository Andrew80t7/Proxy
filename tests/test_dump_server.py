import unittest
import warnings
from http.server import HTTPServer

from Server.dump import (
    sum_numbers,
    fibonacci,
    DumpRequestHandler,
    find_min,
    find_max,
    count_words,
    is_prime,
    factorial,
    celsius_to_fahrenheit,
    is_palindrome,
    reverse_string,
    count_vowels,
    is_even,
)

warnings.filterwarnings("ignore",
                        category=ResourceWarning)


class TestDumpServer(unittest.TestCase):
    def test_fibonacci(self):
        # Тестирование базовых случаев
        self.assertEqual(fibonacci(0),
                         0)
        self.assertEqual(fibonacci(1),
                         1)
        self.assertEqual(fibonacci(10),
                         55)

        # Проверка последовательности
        fib_seq = [fibonacci(n) for n in range(10)]
        self.assertEqual(
            fib_seq,
            [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        )

        # Проверка исключений
        with self.assertRaises(ValueError):
            fibonacci(-1)

    def test_sum_numbers(self):
        # Тестирование основных сценариев
        self.assertEqual(sum_numbers([1, 2, 3]), 6)
        self.assertEqual(sum_numbers([]), 0)
        self.assertEqual(sum_numbers([-1, 0, 1]), 0)

        # Тестирование с дробными числами
        self.assertAlmostEqual(sum_numbers(
            [1.1, 2.2, 3.3]),
            6.6, places=1)

        # Проверка типа данных
        with self.assertRaises(TypeError):
            sum_numbers([1, "2", 3])


class TestFunctions(unittest.TestCase):
    def test_is_even(self):
        self.assertTrue(is_even(4))
        self.assertFalse(is_even(5))
        self.assertTrue(is_even(0))

    def test_count_vowels(self):
        self.assertEqual(count_vowels("Hello World"), 3)
        self.assertEqual(count_vowels("Привет"), 2)
        self.assertEqual(count_vowels("BCDFG"), 0)

    def test_reverse_string(self):
        self.assertEqual(reverse_string("hello"), "olleh")
        self.assertEqual(reverse_string("12345"), "54321")

    def test_is_palindrome(self):
        self.assertTrue(is_palindrome("A man, a plan,"
                                      " a canal: Panama"))
        self.assertFalse(is_palindrome("Hello World"))

    def test_celsius_to_fahrenheit(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32.0)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212.0)

    def test_factorial(self):
        self.assertEqual(factorial(5), 120)
        self.assertEqual(factorial(0), 1)
        with self.assertRaises(ValueError):
            factorial(-5)

    def test_is_prime(self):
        self.assertTrue(is_prime(7919))
        self.assertFalse(is_prime(1))
        self.assertFalse(is_prime(4))

    def test_find_max_min(self):
        nums = [3, 1, 4, 1, 5, 9]
        self.assertEqual(find_max(nums), 9)
        self.assertEqual(find_min(nums), 1)
        self.assertIsNone(find_max([]))

    def test_count_words(self):
        self.assertEqual(count_words("Hello world"),
                         2)
        self.assertEqual(count_words(""), 0)
        self.assertEqual(count_words("   Multiple   spaces   "),
                         2)

    def test_fibonacci(self):
        self.assertEqual(fibonacci(0),
                         0)
        self.assertEqual(fibonacci(1),
                         1)
        self.assertEqual(fibonacci(10),
                         55)
        with self.assertRaises(ValueError):
            fibonacci(-5)

    def test_sum_numbers(self):
        self.assertEqual(sum_numbers([1, 2.5, 3]),
                         6.5)
        self.assertEqual(sum_numbers([]), 0)


def run_dump_server(port=8000):
    server_address = ("", port)
    httpd = HTTPServer(server_address, DumpRequestHandler)
    print(f"Dump download server running on port"
          f" {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    unittest.main(failfast=True)
