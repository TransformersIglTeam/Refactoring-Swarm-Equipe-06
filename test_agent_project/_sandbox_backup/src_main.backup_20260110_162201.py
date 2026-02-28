'''
This module provides functions for basic arithmetic operations.
'''

def add_numbers(a, b):
    try:
        return float(a) + float(b)
    except ValueError as exc:
        raise TypeError("Inputs to add_numbers must be numerical or convertible to numbers.") from exc

def multiply_numbers(a, b):
    try:
        return float(a) * float(b)
    except ValueError as exc:
        raise TypeError("Inputs to multiply_numbers must be numerical or convertible to numbers.") from exc
