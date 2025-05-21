def factorial(num: int):
    """
    Recursive factorial:
     - factorial(0) == 1
     - only non-negative integers allowed
    """
    if not isinstance(num, int):
        raise TypeError(f"factorial() only accepts integers, got {type(num).__name__}")
    if num < 0:
        raise ValueError("factorial() not defined for negative values")
    if num == 0:
        return 1
    return num * factorial(num - 1)
