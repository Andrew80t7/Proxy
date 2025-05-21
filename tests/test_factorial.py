import pytest
from casino.test import factorial


def test_factorial_zero():
    assert factorial(0) == 1


def test_factorial_one():
    assert factorial(1) == 1


@pytest.mark.parametrize("n,expected", [
    (2, 2),
    (3, 6),
    (4, 24),
    (5, 120),
])
def test_factorial_small(n, expected):
    assert factorial(n) == expected


def test_factorial_negative_raises_value_error():
    with pytest.raises(ValueError):
        factorial(-1)


def test_factorial_non_integer_raises_type_error():
    with pytest.raises(TypeError):
        factorial(3.5)
