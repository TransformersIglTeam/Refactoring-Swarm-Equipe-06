'''
This module provides functions for basic arithmetic operations.
'''

def add_numbers(a, b):
    '''
    Adds two numbers together.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of the two numbers.

    Raises:
        TypeError: If inputs are not numerical or convertible to numbers.
    '''
    # Ensure inputs are treated as numbers to prevent TypeError with string concatenation
    # Assuming the intent is arithmetic addition.
    try:
        return float(a) + float(b)
    except ValueError as exc:
        raise TypeError("Inputs to add_numbers must be numerical or convertible to numbers.") from exc

def multiply_numbers(a, b):
    '''
    Multiplies two numbers together.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The product of the two numbers.
    '''
    return a * b
