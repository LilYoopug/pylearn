---
order: 3
exercise: 13
title: pH Levels
xp: 20
module: 3
vars: |
  ph = randint(0, 14)
  if ph < 7:
      kind = 'Acidic'
  elif ph == 7:
      kind = 'Neutral'
  else:
      kind = 'Basic'
  result = f'pH {ph} is {kind}'
expect: "{{result}}"
---

<learn>
`elif` chains several conditions together. Python checks them in order and
runs the **first** one that is true:

```python
if ph < 7:
    print('Acidic')
elif ph == 7:
    print('Neutral')
else:
    print('Basic')
```

Order matters. If you checked `ph > 7` first, a value of 7 would fall through
to the wrong branch.
</learn>

<instructions>
A solution has a pH of **{{ph}}**. Print its classification in this exact
format:

```output
{{result}}
```

- below 7 → `Acidic`
- exactly 7 → `Neutral`
- above 7 → `Basic`
</instructions>

<help>
<hint>Build the line with an f-string: `f'pH {ph} is {kind}'`. Use `elif` so only one branch runs.</hint>
<solution>
ph = {{ph}}
if ph < 7:
    kind = 'Acidic'
elif ph == 7:
    kind = 'Neutral'
else:
    kind = 'Basic'
print(f'pH {ph} is {kind}')
</solution>
</help>
