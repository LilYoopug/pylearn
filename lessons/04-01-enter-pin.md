---
order: 1
exercise: 17
title: Enter PIN
module: 4
check: strict
vars: |
  pin = randint(1000, 9999)
expect: |
  ACCESS GRANTED
---

<learn>
A `while` loop repeats a block **as long as** its condition stays true:

```python
count = 0
while count < 3:
    print(count)
    count = count + 1
```

The two parts that matter: something must change inside the loop, and that
change must eventually make the condition false. Forget the second part and
the loop never ends.
</learn>

<instructions>
Write a `while` loop that keeps asking for the PIN until the correct one,
**{{pin}}**, is entered. When it matches, print `ACCESS GRANTED`.

Because this terminal has no keyboard attached, use a counter instead of
`input()`: loop while a wrong guess remains, then print the message.

```python
pin = {{pin}}
guess = 0
while guess != pin:
    guess = pin
print('ACCESS GRANTED')
```
</instructions>

<help>
<hint>Loop while `guess != pin`. Something inside the loop must move `guess` closer to `pin`, or it never stops.</hint>
<solution>
pin = {{pin}}
guess = 0
while guess != pin:
    guess = pin
print('ACCESS GRANTED')
</solution>
</help>
