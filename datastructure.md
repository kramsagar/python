# Day 4: Data Structures in Python

## Lists
- Ordered, mutable, and allows duplicate elements.

### Syntax & Example:
```python
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")
print(fruits[1])  # banana
fruits[0] = "mango"
```

### Common Operations:
```python
len(fruits)
fruits.insert(1, "kiwi")
fruits.remove("banana")
del fruits[2]
fruits.sort()
```

---

## Tuples
- Ordered, immutable, allows duplicates. Good for fixed collections.

### Syntax & Example:
```python
coordinates = (10, 20)
print(coordinates[0])  # 10
```

### Tuple Unpacking:
```python
x, y = coordinates
```

---

## Dictionaries
- Key-value pairs, unordered (Python 3.6+ maintains insertion order), mutable.

### Syntax & Example:
```python
person = {"name": "Alice", "age": 25}
print(person["name"])
person["age"] = 26
person["city"] = "New York"
```

### Common Methods:
```python
person.keys()
person.values()
person.items()
person.get("name")
person.pop("city")
```

---

## Sets
- Unordered, mutable, no duplicate elements.

### Syntax & Example:
```python
colors = {"red", "green", "blue"}
colors.add("yellow")
colors.discard("green")
```

### Set Operations:
```python
set1 = {1, 2, 3}
set2 = {3, 4, 5}
print(set1.union(set2))
print(set1.intersection(set2))
print(set1.difference(set2))
```

---

## CSV Parsing Exercise
Assume we have `data.csv`:
```
name,age,city
Alice,25,New York
Bob,30,Los Angeles
```

### Code to Parse and Manipulate:
```python
with open('data.csv', 'r') as file:
    lines = file.readlines()
    headers = lines[0].strip().split(',')
    data = [dict(zip(headers, line.strip().split(','))) for line in lines[1:]]

for person in data:
    person['age'] = int(person['age']) + 1
print(data)
```

---

# Day 5: File Handling in Python

## Reading Files
```python
with open('example.txt', 'r') as f:
    content = f.read()
print(content)
```

## Writing Files
```python
with open('output.txt', 'w') as f:
    f.write("Hello, World!\n")
```

## Appending Files
```python
with open('output.txt', 'a') as f:
    f.write("Another line\n")
```

## Reading File Line by Line
```python
with open('example.txt', 'r') as f:
    for line in f:
        print(line.strip())
```

## Working with Binary Files
```python
# Writing binary data
with open('binary_file.bin', 'wb') as f:
    f.write(b'\x00\xFF')

# Reading binary data
with open('binary_file.bin', 'rb') as f:
    data = f.read()
    print(data)
```

## File Existence Check
```python
import os
if os.path.exists('example.txt'):
    print("The file exists!")
else:
    print("The file does not exist!")
```

## File Deletion
```python
os.remove('output.txt')
```

## Directory Operations
```python
os.mkdir('new_directory')
os.chdir('new_directory')
print(os.getcwd())
os.chdir('..')
os.rmdir('new_directory')
```

## Using `with` to Auto-Close Files
```python
with open('auto_close.txt', 'w') as f:
    f.write("This file will auto-close.")
# No need to explicitly call f.close()
```

## Using the `os` Module
The `os` module provides a way to interact with the operating system.

### Common Functions:
```python
import os

print(os.getcwd())  # Current working directory
os.mkdir('new_folder')  # Create directory
os.listdir('.')  # List files
os.remove('output.txt')  # Delete a file
```

### Official Docs:
https://docs.python.org/3/library/os.html

---

# Excel File Operations in Python

To work with Excel files, use the `openpyxl` library (for `.xlsx`) or `pandas` for general data manipulation.

## Install Required Library
```bash
pip install openpyxl pandas
```

## Reading Excel File with `pandas`
```python
import pandas as pd

# Read entire Excel file
df = pd.read_excel('sample.xlsx')
print(df.head())

# Read a specific sheet
df_sheet2 = pd.read_excel('sample.xlsx', sheet_name='Sheet2')
```

## Writing Excel File
```python
# Save DataFrame to Excel
output_df = pd.DataFrame({'Name': ['Alice', 'Bob'], 'Age': [25, 30]})
output_df.to_excel('output.xlsx', index=False)
```

## Working with Multiple Sheets (Writing)
```python
with pd.ExcelWriter('multi_sheet.xlsx') as writer:
    df1.to_excel(writer, sheet_name='Sheet1')
    df2.to_excel(writer, sheet_name='Sheet2')
```

## Reading/Writing Using `openpyxl`
```python
from openpyxl import load_workbook, Workbook

# Reading
wb = load_workbook('sample.xlsx')
sheet = wb['Sheet1']
for row in sheet.iter_rows(values_only=True):
    print(row)

# Writing
wb = Workbook()
sheet = wb.active
sheet.title = "NewSheet"
sheet['A1'] = "Hello"
sheet['B1'] = "World"
wb.save("new_file.xlsx")
```

## List All Sheet Names
```python
wb = load_workbook('sample.xlsx')
print(wb.sheetnames)
```

## Create New Sheet and Write Data
```python
sheet = wb.create_sheet(title="Summary")
sheet['A1'] = "Report Generated"
wb.save("sample.xlsx")
```

## Delete a Sheet
```python
del wb['Sheet2']
wb.save("sample.xlsx")
```

