---
order: 6
exercise: 27
title: Bucket List
module: 5
check: strict
vars: |
  dreams = sample(['see the northern lights', 'learn to sail',
                   'run a marathon', 'visit Japan', 'write a book'], 3)
expect: |
  {{[d.upper() for d in dreams]}}
---

<learn>
Looping over a list and transforming each item is so common that Python has a
short form for it:

```python
names = ['ada', 'alan']
loud = [n.upper() for n in names]     # ['ADA', 'ALAN']
```

That is a **list comprehension** — square brackets, an expression, then
`for ... in ...`. It builds a new list rather than changing the old one.

String methods you will use most: `.upper()`, `.lower()`, `.title()`, and
`.strip()`.
</learn>

<instructions>
Your bucket list:

{{dreams}}

Print every entry in **capitals**, one per line.

```python
dreams = {{dreams}}
for dream in dreams:
    print(dream.upper())
```
</instructions>

<help>
<hint>`print(dream.upper())` inside the loop is all it takes.</hint>
<solution>
dreams = {{dreams}}
for dream in dreams:
    print(dream.upper())
</solution>
</help>
