---
order: 4
exercise: 20
title: 99 Bottles
xp: 25
module: 4
vars: |
  start = randint(3, 6)
expect: |
  {{[f'{n} bottle' + ('' if n == 1 else 's') + ' of pop on the wall' for n in range(start, 0, -1)]}}
---

<learn>
A `while` loop that counts **down** is the mirror of one that counts up:

```python
bottles = 3
while bottles > 0:
    print(bottles)
    bottles = bottles - 1
```

Watch the singular: at 1 bottle the wording changes from "bottles" to
"bottle". Small detail, but it is exactly the kind of thing a program has to
handle explicitly.
</learn>

<instructions>
Start with **{{start}}** bottles of pop and count down to 1, printing one line
per count:

```output
{{start}} bottles of pop on the wall
...
1 bottle of pop on the wall
```

Use `bottles` for the count. The last line must say **bottle**, not bottles.
</instructions>

<help>
<hint>Loop while `bottles > 0`, then decrement. Use an `if` inside for the singular form when `bottles == 1`.</hint>
<solution>
bottles = {{start}}
while bottles > 0:
    if bottles == 1:
        print(f'{bottles} bottle of pop on the wall')
    else:
        print(f'{bottles} bottles of pop on the wall')
    bottles = bottles - 1
</solution>
</help>
