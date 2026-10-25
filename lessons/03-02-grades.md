---
order: 2
exercise: 12
title: Grades
xp: 15
module: 3
vars: |
  grade = randint(30, 100)
  result = 'You passed.' if grade >= 55 else 'You failed.'
expect: "{{result}}"
---

<learn>
A single comparison is often enough:

```python
grade = 58
if grade >= 55:
    print('You passed.')
else:
    print('You failed.')
```

`>=` means "greater than or equal to". Using `>` instead would fail a score of
exactly 55, which is a classic off-by-one bug.
</learn>

<instructions>
A student scored **{{grade}}** out of 100. The pass mark is **55**.

Print `You passed.` or `You failed.` as appropriate.

```python
grade = {{grade}}
if grade >= 55:
    print('You passed.')
else:
    print('You failed.')
```
</instructions>

<help>
<hint>Use `>=` so a score of exactly 55 still passes.</hint>
<solution>
grade = {{grade}}
if grade >= 55:
    print('You passed.')
else:
    print('You failed.')
</solution>
</help>
