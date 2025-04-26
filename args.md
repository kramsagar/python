*args and **kwargs in Python
🔹 What are *args?
*args allows a function to accept any number of positional arguments as a tuple.

✅ Syntax:
python
Copy
Edit
def my_func(*args):
    for arg in args:
        print(arg)
🔹 What are **kwargs?
**kwargs allows a function to accept any number of keyword arguments as a dictionary.

✅ Syntax:
python
Copy
Edit
def my_func(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")
📌 Real-Time Examples
1. 🧾 Logging Utility (*args)
python
Copy
Edit
def log_message(*messages):
    for msg in messages:
        print(f"[LOG]: {msg}")

log_message("Server started", "User logged in", "Error occurred")
Output:
markdown
Copy
Edit
[LOG]: Server started
[LOG]: User logged in
[LOG]: Error occurred
2. 🛒 E-Commerce Order Summary (**kwargs)
python
Copy
Edit
def order_summary(**details):
    print("Order Details:")
    for k, v in details.items():
        print(f"{k}: {v}")

order_summary(product="Laptop", price=75000, status="Shipped")
Output:
vbnet
Copy
Edit
Order Details:
product: Laptop
price: 75000
status: Shipped
3. 💡 Using Both Together
python
Copy
Edit
def describe_person(name, *hobbies, **details):
    print(f"Name: {name}")
    print("Hobbies:")
    for hobby in hobbies:
        print(f" - {hobby}")
    print("Other Details:")
    for key, value in details.items():
        print(f"{key}: {value}")

describe_person("Ravi", "Cricket", "Reading", age=30, city="Hyderabad")
Output:
yaml
Copy
Edit
Name: Ravi
Hobbies:
```markdown
*args and **kwargs in Python

🔹 What are *args?
*args allows a function to accept any number of positional arguments as a tuple.

✅ Syntax:
```python
def my_func(*args):
    for arg in args:
        print(arg)
```

🔹 What are **kwargs?
**kwargs allows a function to accept any number of keyword arguments as a dictionary.

✅ Syntax:
```python
def my_func(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")
```

📌 Real-Time Examples

1. 🧾 Logging Utility (*args)
```python
def log_message(*messages):
    for msg in messages:
        print(f"[LOG]: {msg}")

log_message("Server started", "User logged in", "Error occurred")
```
**Output:**
```
[LOG]: Server started
[LOG]: User logged in
[LOG]: Error occurred
```

2. 🛒 E-Commerce Order Summary (**kwargs)
```python
def order_summary(**details):
    print("Order Details:")
    for k, v in details.items():
        print(f"{k}: {v}")

order_summary(product="Laptop", price=75000, status="Shipped")
```
**Output:**
```
Order Details:
product: Laptop
price: 75000
status: Shipped
```

3. 💡 Using Both Together
```python
def describe_person(name, *hobbies, **details):
    print(f"Name: {name}")
    print("Hobbies:")
    for hobby in hobbies:
        print(f" - {hobby}")
    print("Other Details:")
    for key, value in details.items():
        print(f"{key}: {value}")

describe_person("Ravi", "Cricket", "Reading", age=30, city="Hyderabad")
```
**Output:**
```
Name: Ravi
Hobbies:
 - Cricket
 - Reading
Other Details:
age: 30
city: Hyderabad
```

✅ Summary Table

| Feature   | *args                | **kwargs             |
|-----------|----------------------|----------------------|
| Type      | Tuple                | Dictionary           |
| Use Case  | Multiple positional arguments | Multiple keyword arguments |
| Flexibility | High – can pass any number | High – can pass any number |
| Syntax    | *args                | **kwargs             |
```
 - Reading
Other Details:
age: 30
city: Hyderabad
✅ Summary Table

Feature	*args	**kwargs
Type	Tuple	Dictionary
Use Case	Multiple positional arguments	Multiple keyword arguments
Flexibility	High – can pass any number	High – can pass any number
Syntax	*args	**kwargs