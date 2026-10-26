---
order: 5
exercise: 5
title: Envelope
module: 1
vars: |
  name = choice(['Ada', 'Grace', 'Alan', 'Katherine', 'Linus', 'Margaret'])
  city = choice(['Oslo', 'Lima', 'Kyoto', 'Cairo', 'Lisbon', 'Nairobi'])
  street = choice(['Elm Street', 'Harbour Road', 'Sunset Boulevard', 'Kingsway'])
  number = randint(1, 240)
expect: |
  {{name}}
  {{number}} {{street}}
  {{city}}
---

<learn>
A letter has a shape: the name on its own line, then the street address, then
the city. Your job is to reproduce that shape with `print()`.

This is exactly what the `print()` function is for — one call per line of the
address.
</learn>

<instructions>
Print an envelope address for **{{name}}**, who lives at
**{{number}} {{street}}**, **{{city}}**.

It must be exactly three lines, in this order:

```output
{{name}}
{{number}} {{street}}
{{city}}
```

Note that the number and the street share one line, separated by a space.
</instructions>

<help>
<hint>Three `print()` calls. The middle one has two values in the same string.</hint>
<solution>
print('{{name}}')
print('{{number}} {{street}}')
print('{{city}}')
</solution>
</help>
