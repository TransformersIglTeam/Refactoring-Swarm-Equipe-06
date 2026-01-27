"""Tests for calculator module."""
import pytest
from calculator import (
    add_numbers, subtract_numbers, divide_numbers,
    calculate_average, is_positive, find_max, safe_divide
)


def test_add_numbers():
    assert add_numbers(2, 3) == 5


def test_subtract_numbers():
    assert subtract_numbers(10, 3) == 7


def test_divide_numbers():
    assert divide_numbers(10, 2) == 5.0


def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide_numbers(10, 0)


def test_calculate_average():
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0


def test_is_positive():
    assert is_positive(5) is True
    assert is_positive(-5) is False
    assert is_positive(0) is False


def test_find_max():
    assert find_max([1, 5, 3, 9, 2]) == 9


def test_safe_divide():
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0, default=-1) == -1
