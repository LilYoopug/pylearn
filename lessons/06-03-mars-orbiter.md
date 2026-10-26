---
order: 3
exercise: 30
title: Mars Orbiter
module: 6
vars: |
  days = randint(30, 400)
  hours = days * 24
  minutes = hours * 60
expect: |
  Days: {{days}}
  Hours: {{hours}}
  Minutes: {{minutes}}
---

<learn>
A function with a parameter can be called with many different values, and each
call computes its own answer:

```python
def double(n):
    return n * 2

print(double(5))
print(double(50))
```

The parameter `n` is a local name. It exists only inside the function and does
not clash with anything outside.
</learn>

<instructions>
The orbiter has been flying for **{{days}}** days.

Write a function `convert(days)` that returns the number of hours, then print
all three values:

```output
Days: {{days}}
Hours: {{hours}}
Minutes: {{minutes}}
```

Use the function for the hours; derive minutes from hours.
</instructions>

<help>
<hint>One day is 24 hours, one hour is 60 minutes. Call your function once and store the result.</hint>
<solution>
def convert(days):
    return days * 24

days = {{days}}
hours = convert(days)
print(f'Days: {days}')
print(f'Hours: {hours}')
print(f'Minutes: {hours * 60}')
</solution>
</help>
