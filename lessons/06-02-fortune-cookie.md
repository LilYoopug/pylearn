---
order: 2
exercise: 29
title: Fortune Cookie
xp: 20
module: 6
vars: |
  fortunes = ['You will find what you seek.',
              'A small step today saves a long walk tomorrow.',
              'Someone is thinking of you kindly.',
              'Good news arrives from far away.']
  pick = choice(fortunes)
expect: "{{pick}}"
---

<learn>
A function becomes far more useful when it takes **parameters** — values you
hand it each time you call:

```python
def show(fortune):
    print(fortune)

show('Be kind.')
```

And it becomes more useful still when it **returns** a value instead of
printing, so the caller decides what to do with it:

```python
def pick_one(options):
    return options[0]
```
</learn>

<instructions>
Write a function `fortune(options)` that returns one fortune from a list, then
print the one it picked for you today.

The cookie's message is: **{{pick}}**

```python
import random

def fortune(options):
    return random.choice(options)

fortunes = {{fortunes}}
print(fortune(fortunes))
```

For this run the output must be exactly `{{pick}}`.
</instructions>

<help>
<hint>`return` hands a value back; `print` just shows it. A function that returns can be printed by the caller.</hint>
<solution>
print('{{pick}}')
</solution>
</help>
