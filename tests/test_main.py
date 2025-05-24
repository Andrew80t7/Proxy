import unittest
from main import (is_palindrome,
                  fibonacci,
                  celsius_to_fahrenheit,
                  average,
                  is_anagram,
                  gcd,
                  meters_to_feet,
                  count_vowels,
                  reverse_string,
                  is_prime)


class TestPalindromeFunctions(unittest.TestCase):
    def test_valid_palindromes(self):
        test_cases = [
            ("radar", True),
            ("A man a plan a canal Panama", True),
            ("", True),  # edge case
            ("12321", True),
            ("Was it a car or a cat I saw?", True)
        ]
        for s, expected in test_cases:
            with self.subTest(s=s):
                self.assertEqual(is_palindrome(s), expected)

    def test_non_palindromes(self):
        self.assertFalse(is_palindrome("hello"))
        self.assertFalse(is_palindrome("python"))
        self.assertFalse(is_palindrome("12345"))


class TestFibonacciFunctions(unittest.TestCase):
    def test_base_cases(self):
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(1), 1)

    def test_sequence_values(self):
        self.assertEqual(fibonacci(5), 5)
        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(fibonacci(15), 610)

    def test_negative_input(self):
        with self.assertRaises(ValueError):
            fibonacci(-5)

    def test_large_values(self):
        self.assertEqual(fibonacci(20), 6765)


class TestTemperatureConversion(unittest.TestCase):
    def test_integer_values(self):
        self.assertAlmostEqual(
            celsius_to_fahrenheit(0),
            32.0)
        self.assertAlmostEqual(
            celsius_to_fahrenheit(100),
            212.0)

    def test_float_values(self):
        self.assertAlmostEqual(
            celsius_to_fahrenheit(36.6),
            97.88, places=2)
        self.assertAlmostEqual(
            celsius_to_fahrenheit(-40),
            -40.0)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            celsius_to_fahrenheit("25")
        with self.assertRaises(TypeError):
            celsius_to_fahrenheit([30])

    def test_edge_cases(self):
        self.assertAlmostEqual(
            celsius_to_fahrenheit(273.15),
            523.67,
            delta=0.01)


class TestFunctions(unittest.TestCase):

    # Существующие тесты
    def test_is_palindrome(self):
        self.assertTrue(is_palindrome("A man, a plan, a canal: Panama"))
        self.assertFalse(is_palindrome("Hello"))
        self.assertTrue(is_palindrome(""))
        self.assertFalse(is_palindrome(123))  # Проверка обработки ошибок

    def test_fibonacci(self):
        self.assertEqual(fibonacci(0), 0)
        self.assertEqual(fibonacci(10), 55)
        with self.assertRaises(ValueError):
            fibonacci(-5)

    def test_celsius_to_fahrenheit(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(0),

                               32.0)
        self.assertAlmostEqual(celsius_to_fahrenheit(100),
                               212.0)
        with self.assertRaises(TypeError):
            celsius_to_fahrenheit("100")

    # Новые тесты
    def test_is_prime(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(7919))
        self.assertFalse(is_prime(1))
        self.assertFalse(is_prime(100))

    def test_reverse_string(self):
        self.assertEqual(reverse_string("hello"),
                         "olleh")
        self.assertEqual(reverse_string("12345"),
                         "54321")
        self.assertEqual(reverse_string(""), "")

    def test_count_vowels(self):
        self.assertEqual(count_vowels("Hello World"), 3)
        self.assertEqual(count_vowels("Привет Мир"), 3)
        self.assertEqual(count_vowels("BCDFG"), 0)

    def test_meters_to_feet(self):
        self.assertAlmostEqual(meters_to_feet(1), 3.28084, places=4)
        self.assertAlmostEqual(meters_to_feet(0), 0.0)
        with self.assertRaises(TypeError):
            meters_to_feet("100")

    def test_gcd(self):
        self.assertEqual(gcd(54, 24), 6)
        self.assertEqual(gcd(101, 103), 1)
        self.assertEqual(gcd(0, 5), 5)

    def test_is_anagram(self):
        self.assertTrue(is_anagram("listen", "silent"))
        self.assertTrue(is_anagram("Tom Marvolo Riddle",
                                   "I am Lord Voldemort"))
        self.assertFalse(is_anagram("hello", "world"))

    def test_average(self):
        self.assertAlmostEqual(average([1, 2, 3, 4, 5]), 3.0)
        self.assertAlmostEqual(average([10, -5, 3, 2]), 2.5)
        with self.assertRaises(ValueError):
            average([])


if __name__ == "__main__":
    unittest.main(verbosity=2)
