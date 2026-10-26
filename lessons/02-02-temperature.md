---
order: 2
exercise: 7
title: Temperature
module: 2
check: strict
vars: |
  temp_f = randint(20, 110)
  temp_c = (temp_f - 32) / 1.8
expect: "{{temp_c}}"
---

<learn>
Python is happy to do the arithmetic for you — you only have to write the
formula once.

Fahrenheit to Celsius is:

```
celsius = (fahrenheit - 32) / 1.8
```

Put the numbers in variables, write the formula in terms of those variables,
and print the result. Python does the rest.
</learn>

<instructions>
The temperature today is **{{temp_f}}°F**. Convert it to Celsius and print the
result.

```python
temp_f = {{temp_f}}
temp_c = (temp_f - 32) / 1.8
print(temp_c)
```

Do not round the answer — print it exactly as Python computes it.
</instructions>

<help>
<hint>Subtract 32 first, then divide by 1.8. Parentheses matter: without them Python divides before subtracting.</hint>
<solution>
temp_f = {{temp_f}}
temp_c = (temp_f - 32) / 1.8
print(temp_c)
</solution>
</help>
