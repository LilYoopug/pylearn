---
order: 4
exercise: 42
title: Forty Two
xp: 20
module: 8
vars: |
  target = 42
expect: "{{float(target)}}"
---

<learn>
The `math` module has the maths that is not built in:

```python
import math

print(math.sqrt(144))     # 12.0
print(math.pi)            # 3.141592653589793
print(math.floor(3.9))    # 3
print(math.ceil(3.1))     # 4
```

`math.sqrt` is the readable alternative to `** 0.5`.
</learn>

<instructions>
The answer to everything is **{{target}}**.

Use `math.sqrt` to compute a square root that equals it, then print the
result.

```python
import math

print(math.sqrt({{target ** 2}}))
```
</instructions>

<help>
<hint>Square the target first, then take the square root — the two cancel out.</hint>
<solution>
import math

print(math.sqrt({{target ** 2}}))
</solution>
</help>
