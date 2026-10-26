---
order: 3
exercise: 3
title: Pattern
module: 1
check: output
expect: |
          1
        2 3
      4 5 6
    7 8 9 10
---

<learn>
Each `print()` call ends with a new line. So a series of `print()` calls draws
a series of lines — which means you can draw with text.

The trick to a pattern is the **spaces inside the string**. `'  4 5 6'` is not
the same string as `'4 5 6'`: the first one starts three columns further right.
</learn>

<instructions>
Print this number triangle, exactly four lines, with the spacing shown:

```output
      1
    2 3
  4 5 6
7 8 9 10
```

Each line starts one space further left than the line above it.
</instructions>

<help>
<hint>Four `print()` calls, one per line. Put the leading spaces inside the string, before the first number.</hint>
<solution>
print('      1')
print('    2 3')
print('  4 5 6')
print('7 8 9 10')
</solution>
</help>
