import unittest
from unittest.mock import patch
from main import is_palindrome, fibonacci, celsius_to_fahrenheit


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
        self.assertAlmostEqual(celsius_to_fahrenheit(0), 32.0)
        self.assertAlmostEqual(celsius_to_fahrenheit(100), 212.0)

    def test_float_values(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(36.6), 97.88, places=2)
        self.assertAlmostEqual(celsius_to_fahrenheit(-40), -40.0)

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            celsius_to_fahrenheit("25")
        with self.assertRaises(TypeError):
            celsius_to_fahrenheit([30])

    def test_edge_cases(self):
        self.assertAlmostEqual(celsius_to_fahrenheit(273.15), 523.67, delta=0.01)


if __name__ == "__main__":
    unittest.main(verbosity=2)
