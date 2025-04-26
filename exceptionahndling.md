# Exception Handling in Python

## Built-in Exception Hierarchy

To explore Python's built-in exception hierarchy, you can use:
```python
help("exceptions")
```

---

## Examples of Common Exceptions

Here are some examples of exceptions and when they occur:

| Code Example                     | Exception Type       |
|----------------------------------|----------------------|
| `int("abc")`                     | `ValueError`         |
| `open("file.txt")`               | `FileNotFoundError`  |
| `dict["key"]` (nonexistent key)  | `KeyError`           |
| `1 / 0`                          | `ZeroDivisionError`  |
| `list[100]`                      | `IndexError`         |
| `None.x()`                       | `AttributeError`     |

---

## Using `try-except` with Logging

To handle unknown errors, you can use a `try-except` block. For example:
```python
try:
    risky_code()
except Exception as e:
    print("Caught:", type(e).__name__)
```

---

## Common Exception Types to Know

| Exception Type       | When It Occurs                              |
|----------------------|---------------------------------------------|
| `ValueError`         | Invalid value (e.g., `int("abc")`)         |
| `TypeError`          | Wrong type (e.g., `3 + "hello"`)           |
| `ZeroDivisionError`  | Division by zero                           |
| `FileNotFoundError`  | File not found                             |
| `IndexError`         | List index out of range                    |
| `KeyError`           | Missing key in a dictionary                |
| `AttributeError`     | Missing attribute                          |
| `ImportError`        | Failed to import a module                  |
| `IOError` / `OSError`| File/device-related issues                 |

---

## Temporary Use of a Generic Catch

While debugging, you can use a generic exception handler temporarily:
```python
except Exception as e:
    print(f"Error: {type(e).__name__} - {e}")
```

> **Note:** Avoid using a generic catch in production code as it may hide critical issues.