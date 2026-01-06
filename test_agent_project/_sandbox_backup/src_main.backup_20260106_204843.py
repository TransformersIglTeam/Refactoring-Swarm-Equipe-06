def add_numbers(a, b):
    # Intentional bug: converting second argument to string before adding (concatenation vs addition) or similar
    # Actually let's do a type error bug
    return a + " " + b

def multiply_numbers(a, b):
    return a * b
