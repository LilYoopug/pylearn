---
order: 3
exercise: 24
title: Inventory
xp: 20
module: 5
vars: |
  items = sample(['sword', 'shield', 'potion', 'rope', 'torch', 'map'], 4)
  count = len(items)
expect: |
  {{repr(items)}}
  Total items: {{count}}
---

<learn>
`len()` counts how many things are in a list:

```python
bag = ['sword', 'shield']
print(len(bag))      # 2
```

Two more things you will want constantly:

```python
'sword' in bag       # True  — membership test
bag.sort()           # sorts in place, alphabetically
sorted(bag)          # returns a new sorted list, leaves bag alone
```
</learn>

<instructions>
You are carrying these four items, in this order:

{{items}}

Print the list, then a second line with the total count.

```output
{{items}}
Total items: {{count}}
```

Use `len()` for the count — do not type the number yourself.
</instructions>

<help>
<hint>Print the list first, then an f-string that calls `len()`.</hint>
<solution>
inventory = {{items}}
print(inventory)
print(f'Total items: {len(inventory)}')
</solution>
</help>
