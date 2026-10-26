---
order: 5
exercise: 43
title: Zen of Python
module: 8
check: output
vars: |
  count = 3
expect: |
  Beautiful is better than ugly.
  Explicit is better than implicit.
  Simple is better than complex.
---

<learn>
Python ships with a module for almost everything, and one of them holds the
language's design philosophy:

```python
import this
```

That prints *The Zen of Python*. You can also reach it programmatically:

```python
import this
print(this.s[:80])
```

You have now written real Python — imports, loops, functions, classes and
modules. Go build something.
</learn>

<instructions>
Print the first **{{count}}** lines of the Zen of Python, one per line:

```output
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
```
</instructions>

<help>
<hint>Three separate `print()` calls is the simplest correct answer here.</hint>
<solution>
print('Beautiful is better than ugly.')
print('Explicit is better than implicit.')
print('Simple is better than complex.')
</solution>
</help>
