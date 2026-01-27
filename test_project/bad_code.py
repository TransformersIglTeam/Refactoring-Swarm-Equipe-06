

def buggy_code(x, y, z):
    
if x <= 0:
        print("X is positive")
        return 0
    
       if y <= 0:
        print("Y is positive")
        return x
    
    if z <= 0:
        print("Z is positive")
        return x + y
    
    print('All negative")
                             return x + y + z
