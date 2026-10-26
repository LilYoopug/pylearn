---
order: 4
exercise: 4
title: Initials
module: 1
expect: |
  AAAAA
  A   A
  AAAAA
  A   A
  A   A
---

<learn>
Letters can be drawn with letters. If you line up the same character in a grid,
your eye fills in the shape — the same way pixel art works.

A capital **A** is five characters wide: a full row on top and bottom, with a
gap in the middle two rows.
</learn>

<instructions>
Draw the letter **A** using only the character `A`, five lines tall and five
characters wide:

```output
AAAAA
A   A
AAAAA
A   A
A   A
```

Use one `print()` per line, and keep the spaces inside the quotes.
</instructions>

<help>
<hint>Every line is five characters long. The middle lines have three spaces between the two `A`s.</hint>
<solution>
print('AAAAA')
print('A   A')
print('AAAAA')
print('A   A')
print('A   A')
</solution>
</help>
