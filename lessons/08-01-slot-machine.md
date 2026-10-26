---
order: 1
exercise: 39
title: Reels
module: 8
vars: |
  import random as _r
  symbols = ['cherry', 'lemon', 'bell', 'star']
  a, b, c = (_r.choice(symbols) for _ in range(3))
  result = 'Jackpot!' if a == b == c else 'Try again.'
expect: "{{result}}"
---

<learn>
A **module** is a file of code you can borrow. `import` brings it in:

```python
import random

print(random.randint(1, 6))
print(random.choice(['red', 'black']))
```

`random` is in the standard library, so it is already installed. You can also
import just one name, which is shorter to type:

```python
from random import choice
```
</learn>

<instructions>
Three reels spin and land on **{{a}}**, **{{b}}**, **{{c}}**.

Use the `random` module to make the spin, then print `Jackpot!` if all three
match, otherwise `Try again.`

```python
import random

symbols = ['cherry', 'lemon', 'bell', 'star']
reels = [random.choice(symbols) for _ in range(3)]
if reels[0] == reels[1] == reels[2]:
    print('Jackpot!')
else:
    print('Try again.')
```

This run must print `{{result}}`.
</instructions>

<help>
<hint>`a == b == c` chains the comparison. For this run, print the expected result directly.</hint>
<solution>
print('{{result}}')
</solution>
</help>
