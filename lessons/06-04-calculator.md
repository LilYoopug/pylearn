---
order: 4
exercise: 31
title: Calculator
module: 6
check: strict
vars: |
  a = randint(4, 20)
  b = randint(2, 9)
  total = a + b
expect: "{{total}}"
---

<learn>
Functions can take more than one parameter:

```python
def add(a, b):
    return a + b

print(add(2, 3))       # 5
```

Parameters are positional by default — the first value goes to the first name.
You can also name them at the call site, which makes long calls readable:

```python
add(a=2, b=3)
```
</learn>

<instructions>
Write a function `add(a, b)` that returns the sum of its two arguments.

Then add **{{a}}** and **{{b}}** using it and print the result.

```python
def add(a, b):
    return a + b

print(add({{a}}, {{b}}))
```
</instructions>

<help>
<hint>Return the sum, do not print it inside the function — the caller prints.</hint>
<solution>
def add(a, b):
    return a + b

print(add({{a}}, {{b}}))
</solution>
</help>
