---
order: 4
exercise: 9
title: Pythagorean
module: 2
vars: |
  a = randint(3, 15)
  b = randint(3, 15)
  c = (a ** 2 + b ** 2) ** 0.5
expect: "{{c}}"
---

<learn>
The Pythagorean theorem says that for a right triangle:

```
c² = a² + b²
```

To get `c` on its own you take the square root. Python has no `sqrt` symbol,
but raising to the power `0.5` is exactly the same thing:

```python
c = (a ** 2 + b ** 2) ** 0.5
```

The parentheses around `a ** 2 + b ** 2` matter — the `** 0.5` must apply to
the whole sum, not just the last term.
</learn>

<instructions>
A right triangle has sides **a = {{a}}** and **b = {{b}}**. Print the length
of the hypotenuse `c`.

```python
a = {{a}}
b = {{b}}
c = (a ** 2 + b ** 2) ** 0.5
print(c)
```

Print the value without rounding.
</instructions>

<help>
<hint>Square both sides, add them, then raise the total to the power 0.5.</hint>
<solution>
a = {{a}}
b = {{b}}
c = (a ** 2 + b ** 2) ** 0.5
print(c)
</solution>
</help>
