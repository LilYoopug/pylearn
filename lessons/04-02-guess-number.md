---
order: 2
exercise: 18
title: Guess Number
xp: 20
module: 4
vars: |
  secret = randint(1, 20)
  steps = 0
  guess = 0
  while guess != secret:
      guess = guess + 1
      steps = steps + 1
expect: "{{steps}}"
---

<learn>
A counter is the most useful thing to keep inside a loop. Start it at zero,
add one each pass, and you can report how many times the loop ran:

```python
steps = 0
while steps < 5:
    steps = steps + 1
print(steps)      # 5
```

`steps += 1` is shorthand for `steps = steps + 1`. Both are correct.
</learn>

<instructions>
The secret number is **{{secret}}**. Count how many guesses it takes if you
guess 1, then 2, then 3, and so on until you hit it.

Print the number of guesses.

```python
secret = {{secret}}
steps = 0
guess = 0
while guess != secret:
    guess = guess + 1
    steps = steps + 1
print(steps)
```
</instructions>

<help>
<hint>Start both counters at 0. Increase the guess and the step count inside the loop.</hint>
<solution>
secret = {{secret}}
steps = 0
guess = 0
while guess != secret:
    guess = guess + 1
    steps = steps + 1
print(steps)
</solution>
</help>
