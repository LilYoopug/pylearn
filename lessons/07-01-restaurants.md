---
order: 1
exercise: 34
title: Restaurants
module: 7
vars: |
  name = choice(['Blue Door', 'Sakura', 'Corner Cafe', 'Little Italy'])
  cuisine = choice(['Italian', 'Japanese', 'French', 'Mexican'])
expect: |
  {{name}} serves {{cuisine}} food.
---

<learn>
A **class** is a template for making your own type. `class` + `__init__` is
how you describe what every instance carries:

```python
class Restaurant:
    def __init__(self, name, cuisine):
        self.name = name
        self.cuisine = cuisine
```

`__init__` runs automatically when you create an instance. `self` is the
instance being built — every attribute you hang on `self` sticks to it.
</learn>

<instructions>
Create a class `Restaurant` whose `__init__` takes a name and a cuisine.

Then make one for **{{name}}**, which serves **{{cuisine}}** food, and print:

```output
{{name}} serves {{cuisine}} food.
```

```python
class Restaurant:
    def __init__(self, name, cuisine):
        self.name = name
        self.cuisine = cuisine

place = Restaurant('{{name}}', '{{cuisine}}')
print(f'{place.name} serves {place.cuisine} food.')
```
</instructions>

<help>
<hint>Read the attributes back with `place.name` and `place.cuisine`.</hint>
<solution>
class Restaurant:
    def __init__(self, name, cuisine):
        self.name = name
        self.cuisine = cuisine

place = Restaurant('{{name}}', '{{cuisine}}')
print(f'{place.name} serves {place.cuisine} food.')
</solution>
</help>
