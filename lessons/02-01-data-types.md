---
order: 1
exercise: 6
title: Data Types
module: 2
vars: |
  a = randint(2, 12)
  b = randint(2, 12)
  total = a + b
expect: "{{total}}"
---

<learn>
A **variable** is a name for a value:

```python
age = 42
```

Every value has a **type**. The four you meet first:

| type    | example   | meaning                |
|---------|-----------|------------------------|
| `int`   | `7`       | whole number           |
| `float` | `7.5`     | number with a decimal  |
| `str`   | `'seven'` | text                   |
| `bool`  | `True`    | true or false          |

Once a value is in a variable, you can do arithmetic with it:

```python
a = 3
b = 4
print(a + b)
```

The operators are `+`, `-`, `*`, `/`, `**` (power), and `%` (remainder).
</learn>

<instructions>
Store **{{a}}** in a variable and **{{b}}** in another variable, then print
their **sum**.

```python
a = {{a}}
b = {{b}}
print(a + b)
```

The terminal should show a single number.
</instructions>

<help>
<hint>Make two variables, then print the expression `a + b` — do not add the numbers yourself.</hint>
<solution>
a = {{a}}
b = {{b}}
print(a + b)
</solution>
</help>
