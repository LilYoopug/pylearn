---
order: 4
exercise: 25
title: Reading
module: 5
check: strict
vars: |
  books = sample(['Dune', 'Emma', 'Beloved', 'Ulysses', 'Dracula', 'Middlemarch'], 3)
  target = books[1]
expect: "{{target}}"
---

<learn>
Lists keep their order, so the first thing you added stays first. That makes
them natural for a reading list: the order is the queue.

To find something without knowing its position:

```python
books = ['Dune', 'Emma']
print('Dune' in books)        # True
print(books.index('Emma'))    # 1
```

`index()` gives you the position; `in` just tells you yes or no.
</learn>

<instructions>
Your reading list holds:

{{books}}

Print the **second** book on the list, using its index rather than a hardcoded
string.

```python
books = {{books}}
print(books[1])
```
</instructions>

<help>
<hint>Indexing starts at 0, so the second item is at index 1.</hint>
<solution>
books = {{books}}
print(books[1])
</solution>
</help>
