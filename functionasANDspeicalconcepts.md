Day 6: Functions and Lambda Expressions in Python
Defining a Function
python
Copy
Edit
def greet(name):
    return f"Hello, {name}!"
Calling a Function
python
Copy
Edit
print(greet("Alice"))
Function with Default Argument
python
Copy
Edit
def power(base, exponent=2):
    return base ** exponent

print(power(3))       # 9
print(power(2, 3))    # 8
Function with Multiple Arguments
python
Copy
Edit
def add(a, b):
    return a + b
*args and **kwargs
python
Copy
Edit
def print_args(*args):
    for arg in args:
        print(arg)

def print_kwargs(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")
Returning Multiple Values
python
Copy
Edit
def get_coordinates():
    return 10, 20

x, y = get_coordinates()
Lambda Functions
Anonymous functions, useful for short operations.

python
Copy
Edit
square = lambda x: x * x
print(square(5))  # 25
Lambda with map(), filter(), reduce()
python
Copy
Edit
nums = [1, 2, 3, 4, 5]

# map
squared = list(map(lambda x: x**2, nums))

# filter
evens = list(filter(lambda x: x % 2 == 0, nums))

# reduce
from functools import reduce
sum_all = reduce(lambda x, y: x + y, nums)
Nested Functions
python
Copy
Edit
def outer():
    def inner():
        return "Inner function"
    return inner()
    # Day 6: Functions and Lambda Expressions in Python

    ## Defining a Function

    ```python
    def greet(name):
        return f"Hello, {name}!"
    ```

    ## Calling a Function

    ```python
    print(greet("Alice"))
    ```

    ## Function with Default Argument

    ```python
    def power(base, exponent=2):
        return base ** exponent

    print(power(3))       # 9
    print(power(2, 3))    # 8
    ```

    ## Function with Multiple Arguments

    ```python
    def add(a, b):
        return a + b
    ```

    ## *args and **kwargs

    ```python
    def print_args(*args):
        for arg in args:
            print(arg)

    def print_kwargs(**kwargs):
        for key, value in kwargs.items():
            print(f"{key}: {value}")
    ```

    ## Returning Multiple Values

    ```python
    def get_coordinates():
        return 10, 20

    x, y = get_coordinates()
    ```

    ## Lambda Functions

    Anonymous functions, useful for short operations.

    ```python
    square = lambda x: x * x
    print(square(5))  # 25
    ```

    ## Lambda with `map()`, `filter()`, `reduce()`

    ```python
    nums = [1, 2, 3, 4, 5]

    # map
    squared = list(map(lambda x: x**2, nums))

    # filter
    evens = list(filter(lambda x: x % 2 == 0, nums))

    # reduce
    from functools import reduce
    sum_all = reduce(lambda x, y: x + y, nums)
    ```

    ## Nested Functions

    ```python
    def outer():
        def inner():
            return "Inner function"
        return inner()

    print(outer())
    ```

    ## Docstrings

    ```python
    def multiply(a, b):
        """Returns the product of a and b"""
        return a * b
    ```
print(outer())
Docstrings
python
Copy
Edit
def multiply(a, b):
    """Returns the product of a and b"""
    return a * b