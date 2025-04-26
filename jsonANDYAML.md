# JSON and YAML Parsing in Python

## JSON Parsing

JSON (JavaScript Object Notation) is a lightweight data format used for data exchange. In Python, you can easily work with JSON using the `json` module.

### Loading JSON from String

```python
import json

json_data = '{"name": "Alice", "age": 25, "city": "New York"}'
data = json.loads(json_data)
print(data)
print(data['name'])
```

### Loading JSON from File

```python
with open('data.json', 'r') as f:
    data = json.load(f)
print(data)
```

### Writing JSON to File

```python
person = {"name": "Bob", "age": 30, "city": "Los Angeles"}

with open('person.json', 'w') as f:
    json.dump(person, f, indent=4)
```

### Parsing Complex JSON

```python
complex_json = '''
{
    "name": "John",
    "contact": {
        "email": "john@example.com",
        "phone": "1234567890"
    },
    "hobbies": ["reading", "traveling"]
}
'''
data = json.loads(complex_json)
print(data['contact']['email'])
print(data['hobbies'][1])
```

### Convert Python Object to JSON String

```python
person = {"name": "Eve", "age": 22}
json_string = json.dumps(person)
print(json_string)
```

## YAML Parsing

YAML (YAML Ain't Markup Language) is human-readable and often used for configuration files. You can work with YAML using the `PyYAML` library.

### Install PyYAML

```bash
pip install pyyaml
```

### Loading YAML from String

```python
import yaml

yaml_data = '''
name: Alice
age: 25
city: New York
'''
data = yaml.safe_load(yaml_data)
print(data)
print(data['city'])
```

### Loading YAML from File

```python
with open('data.yaml', 'r') as file:
    data = yaml.safe_load(file)
print(data)
```

### Writing YAML to File

```python
person = {'name': 'Bob', 'age': 30, 'city': 'Los Angeles'}

with open('person.yaml', 'w') as file:
    yaml.dump(person, file)
```

### Parsing Complex YAML

```python
yaml_content = '''
person:
  name: John
  contact:
    email: john@example.com
    phone: 1234567890
  hobbies:
    - reading
    - traveling
'''
data = yaml.safe_load(yaml_content)
print(data['person']['contact']['phone'])
print(data['person']['hobbies'][0])
```

### Convert Python Object to YAML String

```python
person = {'name': 'Eve', 'age': 22}
yaml_string = yaml.dump(person)
print(yaml_string)
```
