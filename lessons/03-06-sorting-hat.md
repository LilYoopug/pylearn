---
order: 6
exercise: 16
title: House Sorter
xp: 25
module: 3
vars: |
  score = randint(0, 100)
  if score >= 90:
      house = 'Gryffindor'
  elif score >= 75:
      house = 'Ravenclaw'
  elif score >= 60:
      house = 'Hufflepuff'
  else:
      house = 'Slytherin'
expect: "{{house}}"
---

<learn>
A long `elif` ladder lets you grade something into bands. Each `elif` only
gets checked if every earlier condition was false — which means you do **not**
need to repeat the upper bound:

```python
if score >= 90:
    house = 'Gryffindor'
elif score >= 75:      # score < 90 is already guaranteed here
    house = 'Ravenclaw'
```

Putting the highest band first is what makes the shorter conditions correct.
</learn>

<instructions>
The house sorter reads a score of **{{score}}**.

| score      | house       |
|------------|-------------|
| 90 or more | Gryffindor  |
| 75 or more | Ravenclaw   |
| 60 or more | Hufflepuff  |
| below 60   | Slytherin   |

Print the house name only.
</instructions>

<help>
<hint>Start from the highest band. Each `elif` only needs its lower bound because the higher ones already failed.</hint>
<solution>
score = {{score}}
if score >= 90:
    house = 'Gryffindor'
elif score >= 75:
    house = 'Ravenclaw'
elif score >= 60:
    house = 'Hufflepuff'
else:
    house = 'Slytherin'
print(house)
</solution>
</help>
