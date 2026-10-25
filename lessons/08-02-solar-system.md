---
order: 2
exercise: 40
title: Solar System
xp: 25
module: 8
vars: |
  planet = choice(['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter'])
  distance = {'Mercury': 57.9, 'Venus': 108.2, 'Earth': 149.6,
              'Mars': 227.9, 'Jupiter': 778.6}[planet]
expect: |
  {{planet}} is {{distance}} million km from the Sun.
---

<learn>
Importing your **own** module works the same way: put the code in a `.py`
file, then `import` it by filename (without the `.py`).

```python
# planets.py
DATA = {'Earth': 149.6}

# main.py
import planets
print(planets.DATA['Earth'])
```

A dictionary is the natural fit for "look something up by name":

```python
lookup = {'Mercury': 57.9}
print(lookup['Mercury'])
```
</learn>

<instructions>
Using a dictionary of distances, look up **{{planet}}** and print:

```output
{{planet}} is {{distance}} million km from the Sun.
```

```python
distances = {'Mercury': 57.9, 'Venus': 108.2, 'Earth': 149.6,
             'Mars': 227.9, 'Jupiter': 778.6}
planet = '{{planet}}'
print(f'{planet} is {distances[planet]} million km from the Sun.')
```
</instructions>

<help>
<hint>Index the dictionary with the planet name to get its distance.</hint>
<solution>
distances = {'Mercury': 57.9, 'Venus': 108.2, 'Earth': 149.6,
             'Mars': 227.9, 'Jupiter': 778.6}
planet = '{{planet}}'
print(f'{planet} is {distances[planet]} million km from the Sun.')
</solution>
</help>
