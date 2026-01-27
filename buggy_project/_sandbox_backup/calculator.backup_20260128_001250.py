"""
Calculator module with bugs to be fixed by the Refactoring Swarm.
"""


def add_numbers(a, b):
    """Add two numbers. BUG: No type checking."""
    return a + b


def subtract_numbers(a, b):
    """Subtract b from a. BUG: Returns b-a instead of a-b."""
    return b - a


def divide_numbers(a, b):
    """Divide a by b. BUG: No zero check."""
    return a / b


def calculate_average(numbers):
    """Calculate average. BUG: Missing return statement."""
    total = sum(numbers)
    avg = total / len(numbers)


def is_positive(number):
    """Check if positive. BUG: Logic is inverted."""
    if number <= 0:
        return True
    return False


def find_max(numbers):
    """Find max. BUG: Returns min instead."""
    result = numbers[0]
    for num in numbers:
        if num < result:
            result = num
    return result


def safe_divide(a, b, default=0):
    """Safe divide. BUG: Returns default instead of result."""
    if b == 0:
        return default
    result = a / b
    return default
