---
order: 5
exercise: 21
title: Fizz Buzz
xp: 25
module: 4
vars: |
  limit = randint(5, 9)
expect: |
  {{[('FizzBuzz' if i % 15 == 0 else 'Fizz' if i % 3 == 0 else 'Buzz' if i % 5 == 0 else str(i)) for i in range(1, limit + 1)]}}
---

<learn>
Fizz Buzz is the classic test of two ideas: a loop, and the `%` (remainder)
operator.

```python
7 % 3     # 1, because 7 = 2*3 + 1
9 % 3     # 0, so 9 is divisible by 3
```

A number is divisible by something when the remainder is zero.

The one subtlety: numbers divisible by **both** 3 and 5 must print `FizzBuzz`,
so that check has to come **first** in the `if` chain.
</learn>

<instructions>
For every number from 1 to **{{limit}}**, print:

- `FizzBuzz` if divisible by both 3 and 5
- `Fizz` if divisible by 3
- `Buzz` if divisible by 5
- the number itself otherwise

```python
for i in range(1, {{limit}} + 1):
    if i % 15 == 0:
        print('FizzBuzz')
    elif i % 3 == 0:
        print('Fizz')
    elif i % 5 == 0:
        print('Buzz')
    else:
        print(i)
```
</instructions>

<help>
<hint>Check divisibility by 15 first — it covers "both 3 and 5" in one test.</hint>
<solution>
for i in range(1, {{limit}} + 1):
    if i % 15 == 0:
        print('FizzBuzz')
    elif i % 3 == 0:
        print('Fizz')
    elif i % 5 == 0:
        print('Buzz')
    else:
        print(i)
</solution>
</help>
