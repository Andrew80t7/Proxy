import unittest
import warnings

from Server.dump import (
    sum_numbers,
    fibonacci,
    factorial)

warnings.filterwarnings("ignore",
                        category=ResourceWarning)


class TestDumpServer(unittest.TestCase):
    def test_factorial(self):
        # Тестирование нормальных случаев
        self.assertEqual(factorial(0),
                         1)
        self.assertEqual(factorial(1),
                         1)
        self.assertEqual(factorial(5),
                         120)

        # Тестирование исключений
        with self.assertRaises(ValueError) as context:
            factorial(-5)
        self.assertEqual(str(context.exception),
                         "Factorial"
                         " is not defined for"
                         " negative numbers")

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

    def test_edge_cases(self):
        # Комплексные пограничные случаи
        self.assertEqual(factorial(20),
                         2432902008176640000)
        self.assertEqual(fibonacci(20), 6765)
        self.assertEqual(sum_numbers([1e6, 2e6, 3e6]), 6e6)


if __name__ == "__main__":
    unittest.main(failfast=True)
