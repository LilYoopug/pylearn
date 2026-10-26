---
order: 1
exercise: 11
title: Coin Flip
module: 3
vars: |
  guess = choice(['Heads', 'Tails'])
  flip = choice(['Heads', 'Tails'])
  result = 'You win!' if guess == flip else 'You lose!'
expect: "{{result}}"
---

<learn>
`if` runs a block only when a condition is true, and `else` covers everything
that is not:

```python
if guess == flip:
    print('You win!')
else:
    print('You lose!')
```

Two things to notice: the line ends with a colon, and the block underneath is
**indented**. Python uses indentation to know what belongs to the `if` —
there are no braces.

`==` compares two values. A single `=` assigns. Mixing them up is the most
common beginner mistake.
</learn>

<instructions>
A coin is flipped and lands on **{{flip}}**. You guessed **{{guess}}**.

Print `You win!` if the guess matches, otherwise print `You lose!`.

```python
guess = '{{guess}}'
flip = '{{flip}}'
if guess == flip:
    print('You win!')
else:
    print('You lose!')
```
</instructions>

<help>
<hint>Compare the two strings with `==`. Both branches need their own `print`, indented four spaces.</hint>
<solution>
guess = '{{guess}}'
flip = '{{flip}}'
if guess == flip:
    print('You win!')
else:
    print('You lose!')
</solution>
</help>
