'''
This module provides functions for basic arithmetic operations.
'''

def add_numbers(a, b):
    """Adds two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.

    Raises:
        TypeError: If inputs are not numerical or convertible to numbers.
    """
    try:
        return float(a) + float(b)
    except ValueError as exc:
        raise TypeError("Inputs must be numerical.") from exc

def multiply_numbers(a, b):
    """Multiplies two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of a and b.

    Raises:
        TypeError: If inputs are not numerical or convertible to numbers.
    """
    try:
        return float(a) * float(b)
    except ValueError as exc:
        raise TypeError("Inputs must be numerical.") from exc
