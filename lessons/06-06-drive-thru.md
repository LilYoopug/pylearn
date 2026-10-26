---
order: 6
exercise: 33
title: Drive-Thru
module: 6
check: strict
vars: |
  item = choice(['burger', 'fries', 'shake', 'taco'])
  price = randint(3, 12)
  total = price * 2
expect: |
  You ordered {{item}}.
  Total: {{total}}
---

<learn>
Functions can take a **default** parameter, so callers only pass what they
need to change:

```python
def order(item, quantity=1):
    return f'{quantity}x {item}'

print(order('burger'))          # 1x burger
print(order('burger', 2))       # 2x burger
```

The default is written once, in the `def` line, with `=`.
</learn>

<instructions>
Write a function `order(item, quantity=1)` that returns a sentence describing
the order. Call it for **2× {{item}}** and print:

```output
You ordered {{item}}.
Total: {{total}}
```

Each item costs **{{price}}**.
</instructions>

<help>
<hint>Call `order('{{item}}', 2)` for the first line. Multiply price by quantity for the total.</hint>
<solution>
def order(item, quantity=1):
    return f'You ordered {item}.'

print(order('{{item}}', 2))
print(f'Total: { {{price}} * 2 }')
</solution>
</help>
