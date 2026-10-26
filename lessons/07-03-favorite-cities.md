---
order: 3
exercise: 36
title: Favorite Cities
module: 7
vars: |
  cities = sample(['Tokyo', 'Lisbon', 'Cairo', 'Oslo', 'Quito', 'Perth'], 3)
expect: |
  {{cities}}
---

<learn>
A list of objects is how you model many things of the same kind:

```python
class City:
    def __init__(self, name):
        self.name = name

places = [City('Tokyo'), City('Oslo')]
for place in places:
    print(place.name)
```

Everything you already know about lists works — indexing, `len()`, loops,
comprehensions.
</learn>

<instructions>
Create a class `City` holding a `name`, then build a list with these three
cities:

{{cities}}

Print each name on its own line.

```python
class City:
    def __init__(self, name):
        self.name = name

places = [City(name) for name in {{cities}}]
for place in places:
    print(place.name)
```
</instructions>

<help>
<hint>Build the objects in a list, then loop and print `.name`.</hint>
<solution>
class City:
    def __init__(self, name):
        self.name = name

places = [City(name) for name in {{cities}}]
for place in places:
    print(place.name)
</solution>
</help>
