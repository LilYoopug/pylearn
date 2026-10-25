---
order: 3
exercise: 41
title: Countdown
xp: 20
module: 8
vars: |
  start = randint(3, 7)
expect: |
  {{list(range(start, 0, -1))}}
  Liftoff!
---

<learn>
`range()` takes three arguments: start, stop, and step.

```python
range(5, 0, -1)     # 5, 4, 3, 2, 1
```

The **stop** value is never included. A negative step counts down, which is
exactly what a countdown needs.
</learn>

<instructions>
Count down from **{{start}}** to 1, one number per line, then print `Liftoff!`.

```output
{{list(range(start, 0, -1))}}
Liftoff!
```

```python
for n in range({{start}}, 0, -1):
    print(n)
print('Liftoff!')
```
</instructions>

<help>
<hint>`range(start, 0, -1)` stops before 0, so it ends at 1.</hint>
<solution>
for n in range({{start}}, 0, -1):
    print(n)
print('Liftoff!')
</solution>
</help>
