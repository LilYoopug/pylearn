---
order: 5
exercise: 32
title: Stock Value
xp: 25
module: 6
vars: |
  price = randint(20, 300)
  shares = randint(2, 40)
  value = price * shares
expect: "{{value}}"
---

<learn>
A function can call another function. Splitting a calculation into small named
pieces is what makes a program easy to change later:

```python
def total(price, shares):
    return price * shares

def report(price, shares):
    return f'Value: {total(price, shares)}'
```

Each function does one thing, and the names say what that thing is.
</learn>

<instructions>
You own **{{shares}}** shares at **{{price}}** each.

Write a function `value(price, shares)` that returns the total worth, then
print the number.

```python
def value(price, shares):
    return price * shares

print(value({{price}}, {{shares}}))
```
</instructions>

<help>
<hint>Multiply the two parameters and return the result.</hint>
<solution>
def value(price, shares):
    return price * shares

print(value({{price}}, {{shares}}))
</solution>
</help>
