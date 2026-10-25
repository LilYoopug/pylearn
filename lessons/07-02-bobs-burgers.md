---
order: 2
exercise: 35
title: Menu Board
xp: 25
module: 7
vars: |
  item = choice(['burger', 'fries', 'shake'])
  price = randint(4, 15)
expect: |
  {{item}}: ${{price}}
---

<learn>
A class can also hold **methods** — functions that belong to the instance:

```python
class Menu:
    def __init__(self, item, price):
        self.item = item
        self.price = price

    def label(self):
        return f'{self.item}: ${self.price}'
```

The method takes `self` so it can read the instance's own attributes. Call it
with `menu.label()` — no argument, Python passes `self` for you.
</learn>

<instructions>
Write a class `Menu` with `__init__(self, item, price)` and a method
`label(self)` that returns `"{item}: ${price}"`.

Make one entry for **{{item}}** at **{{price}}** dollars and print its label.

```python
class Menu:
    def __init__(self, item, price):
        self.item = item
        self.price = price

    def label(self):
        return f'{self.item}: ${self.price}'

print(Menu('{{item}}', {{price}}).label())
```
</instructions>

<help>
<hint>The method returns the string; `print()` at the call site shows it.</hint>
<solution>
class Menu:
    def __init__(self, item, price):
        self.item = item
        self.price = price

    def label(self):
        return f'{self.item}: ${self.price}'

print(Menu('{{item}}', {{price}}).label())
</solution>
</help>
