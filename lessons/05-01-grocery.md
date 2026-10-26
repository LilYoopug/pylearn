---
order: 1
exercise: 22
title: Grocery
module: 5
check: strict
vars: |
  items = sample(['milk', 'bread', 'eggs', 'rice', 'apples', 'coffee'], 3)
expect: |
  {{items}}
---

<learn>
A **list** holds several values in order:

```python
shopping = ['milk', 'bread', 'eggs']
```

Square brackets, items separated by commas. To get one item out, use its
**index** — and indexing starts at `0`, not `1`:

```python
print(shopping[0])     # milk
print(shopping[-1])    # eggs, counting from the end
```

You can loop over a list directly, without any index:

```python
for item in shopping:
    print(item)
```
</learn>

<instructions>
Create a list containing exactly these three items, in this order:

{{items}}

Then print each item on its own line.

```python
shopping = {{items}}
for item in shopping:
    print(item)
```
</instructions>

<help>
<hint>One `print` per item. A `for` loop over the list is shorter than three separate prints.</hint>
<solution>
shopping = {{items}}
for item in shopping:
    print(item)
</solution>
</help>
