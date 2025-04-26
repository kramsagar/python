
# Python Variables, Loops, and Advanced Concepts - In-Depth Notes

## 1. Loops in Python

Loops allow us to execute a block of code repeatedly. Python supports two main types of loops:

### `for` Loop

Used to iterate over a sequence (like list, tuple, string, or range).

#### Syntax:
```python
for variable in sequence:
    # code block
```
#### Example:
```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```
**Explanation:** The variable `fruit` takes the value of each item in the `fruits` list one at a time.

### `while` Loop

Executes a block of code as long as a condition is `True`.

#### Syntax:
```python
while condition:
    # code block
```
#### Example:
```python
count = 0
while count < 3:
    print("Count is", count)
    count += 1
```
**Explanation:** This loop prints the count and increments it until it reaches 3.

### `break`, `continue`, and `else`

- `break`: Exits the loop prematurely.
- `continue`: Skips the current iteration and moves to the next.
- `else`: Executes after the loop completes normally (not with `break`).

```python
for i in range(5):
    if i == 3:
        break
    print(i)

for i in range(5):
    if i == 3:
        continue
    print(i)

for i in range(3):
    print(i)
else:
    print("Loop completed")
```

---

## 2. Variable Types and Scopes

### Local Variable

Defined within a function and accessible only inside it.

```python
def my_func():
    x = 10  # local to this function
    print(x)
```

### Global Variable

Declared outside any function and accessible anywhere.

```python
x = 5

def my_func():
    global x
    x = x + 1
    print(x)
```

**Use case:** Useful for shared configuration, counters, etc. But use sparingly to avoid bugs.

### Instance Variable

Belongs to an object and is prefixed with `self`.

```python
class Dog:
    def __init__(self, name):
        self.name = name  # instance variable
```

### Class Variable (Static Variable)

Shared among all instances of the class.

```python
class Dog:
    species = "Canine"  # class/static variable

    def __init__(self, name):
        self.name = name
```

**Difference:** Changing `self.name` affects only one object, but changing `Dog.species` affects all.

---

## 3. Dynamic vs Static Typing

### Dynamic Typing (Python's nature)

Variables can change types during execution.

```python
x = 5       # x is int
x = "text"  # x becomes str
```

**Pros:** Flexibility. **Cons:** Potential for runtime errors.

### Static Variables in Classes

Used to store state shared across all instances.

```python
class Counter:
    count = 0

    def __init__(self):
        Counter.count += 1
```

---

## 4. Advanced Variables

### Mutable vs Immutable

- **Immutable**: Cannot change the value once created — `int`, `str`, `tuple`
- **Mutable**: Can change — `list`, `dict`, `set`

```python
x = [1, 2, 3]
y = x
x.append(4)
print(y)  # [1, 2, 3, 4]
```

### Variable Packing and Unpacking

Allows collecting or distributing values across variables.

```python
a, b, *rest = [1, 2, 3, 4, 5]
print(a, b)     # 1 2
print(rest)     # [3, 4, 5]
```

**Real-world usage:**
- Argument unpacking in functions
- Processing logs or records with dynamic fields

### `global` Inside Nested Functions

Allows inner function to modify outermost variable (module-level).

```python
count = 0

def outer():
    global count
    count += 1

outer()
print(count)  # 1
```

**Use case:** Modifying configuration values shared across multiple functions.

### `nonlocal` Keyword

Used in nested functions to refer to the variable in the nearest enclosing scope (not global).

```python
def outer():
    x = 10
    def inner():
        nonlocal x
        x += 5
    inner()
    print(x)  # 15
outer()
```

**Use case:** Used in closures, decorators, counters, etc.

```python
def retry(max_attempts):
    attempts = 0
    def wrapper():
        nonlocal attempts
        attempts += 1
        print(f"Attempt {attempts}")
    return wrapper

retry_fn = retry(3)
retry_fn()
retry_fn()
```

---

## 5. Best Practices

- Prefer local variables for encapsulation.
- Use `global` only when absolutely necessary.
- Understand scope resolution (LEGB: Local, Enclosing, Global, Built-in).
- Use class variables for static data.
- Embrace dynamic typing but validate types when needed.
- Use `nonlocal` when designing closures that manage state.

---

## 6. Summary Table

| Type           | Scope       | Lifetime        | Mutable? | Real-life Use                |
|----------------|-------------|-----------------|----------|------------------------------|
| Local          | Function    | Until function ends | Yes/No   | Temporary calculations       |
| Global         | Module      | Program-wide     | Yes/No   | App-wide settings            |
| Instance       | Object      | As long as object exists | Yes | Per-user/session data       |
| Class (Static) | Class       | Until program ends | Yes/No | Shared counters, defaults   |
| Dynamic Type   | -           | Runtime          | Yes/No   | Any scripting or automation  |

---
