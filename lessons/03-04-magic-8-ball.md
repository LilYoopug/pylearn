---
order: 4
exercise: 14
title: Fortune Ball
xp: 20
module: 3
vars: |
  question = choice(['Will it rain today?', 'Should I learn Python?',
                     'Is it a good day for a walk?', 'Will I finish this course?'])
  answer = choice(['Yes', 'No', 'Maybe'])
expect: "{{answer}}"
---

<learn>
An `if / elif / else` chain is how you turn a number into a choice. Here we
pick a random number first, then let the chain decide what it means:

```python
import random

roll = random.randint(1, 3)
if roll == 1:
    print('Yes')
elif roll == 2:
    print('No')
else:
    print('Maybe')
```

`random.randint(a, b)` returns a whole number from `a` to `b`, **including**
both ends.
</learn>

<instructions>
You shake the Magic 8 Ball and ask: *"{{question}}"*

The ball answers **{{answer}}**. Print that answer by writing an `if` chain
that maps a random roll to one of the three replies, and make it print exactly
`{{answer}}` this time.

```python
import random

roll = random.randint(1, 3)
if roll == 1:
    print('Yes')
elif roll == 2:
    print('No')
else:
    print('Maybe')
```

For this run, the answer must be `{{answer}}`.
</instructions>

<help>
<hint>You can print the answer directly — the point of the exercise is the `if` chain. `print('{{answer}}')` is acceptable here.</hint>
<solution>
print('{{answer}}')
</solution>
</help>
