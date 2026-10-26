---
order: 3
exercise: 19
title: Detention
module: 4
check: strict
vars: |
  lines = randint(3, 7)
expect: |
  {{["I will not talk in class."] * lines}}
---

<learn>
The classic punishment loop writes the same line many times:

```python
for i in range(3):
    print('I will not talk in class.')
```

`range(3)` produces `0, 1, 2` — three values, so the body runs three times.
The loop variable `i` is available inside, but you do not have to use it.
</learn>

<instructions>
Write the line `I will not talk in class.` exactly **{{lines}}** times, one per
line.

```python
for i in range({{lines}}):
    print('I will not talk in class.')
```
</instructions>

<help>
<hint>`range(n)` runs the body `n` times. Do not print anything else.</hint>
<solution>
for i in range({{lines}}):
    print('I will not talk in class.')
</solution>
</help>
