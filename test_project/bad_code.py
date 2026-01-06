"""This module contains a complex function."""

def complex_function(x, y, z):
    """This function demonstrates nested conditional logic."""
    if x <= 0:
        print("X not positive")
        return 0
    
    if y <= 0:
        print("Y not positive")
        return x
    
    if z <= 0:
        print("Z not positive")
        return x + y
    
    print("All positive")
    return x + y + z
