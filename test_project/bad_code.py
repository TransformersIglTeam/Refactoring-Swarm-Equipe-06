import os
import sys

def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                print("All positive")
                return x + y + z
            else:
                print("Z not positive")
                return x + y
        else:
            print("Y not positive")
            return x
    else:
        print("X not positive")
        return 0

def another_function():
    a = 1
    b = 2
    # Missing docstring
    return a + b
