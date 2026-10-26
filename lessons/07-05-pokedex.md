---
order: 5
exercise: 38
title: Monster Index
module: 7
check: strict
vars: |
  mons = sample(['Bulbasaur', 'Charmander', 'Squirtle', 'Pikachu', 'Eevee'], 2)
expect: |
  {{[f'{n + 1}. {m}' for n, m in enumerate(mons)]}}
---

<learn>
Two useful extras on classes:

```python
class Pokemon:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name
```

`__str__` decides what `print(obj)` shows — without it you would see
`<Pokemon object at 0x...>`, which tells you nothing.
</learn>

<instructions>
Create a class `Pokemon` with a `name` and a `__str__` that returns it.

Then build entries for these two and print a numbered index:

```output
{{[f'{n + 1}. {m}' for n, m in enumerate(mons)]}}
```

```python
class Pokemon:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

mons = [Pokemon(name) for name in {{mons}}]
for number, mon in enumerate(mons, start=1):
    print(f'{number}. {mon}')
```
</instructions>

<help>
<hint>`__str__` must return a string, not print one. With it defined, `{mon}` works inside an f-string.</hint>
<solution>
class Pokemon:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

mons = [Pokemon(name) for name in {{mons}}]
for number, mon in enumerate(mons, start=1):
    print(f'{number}. {mon}')
</solution>
</help>
