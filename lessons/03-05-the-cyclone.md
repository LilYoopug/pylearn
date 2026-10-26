---
order: 5
exercise: 15
title: Ride Check
module: 3
vars: |
  height = randint(120, 200)
  credits = randint(0, 10)
  if height < 137 or credits < 5:
      result = 'Sorry, you cannot ride.'
  else:
      result = 'Enjoy the ride!'
expect: "{{result}}"
---

<learn>
`or` and `and` join two conditions into one:

```python
if height < 137 or credits < 5:
    print('Sorry, you cannot ride.')
else:
    print('Enjoy the ride!')
```

- `or` is true when **at least one** side is true.
- `and` is true only when **both** sides are true.

For a ride with two rules, being rejected by *either* rule is enough — so `or`
is the right connector here.
</learn>

<instructions>
A rider is **{{height}} cm** tall and has **{{credits}}** ride credits.

To ride you need to be at least 137 cm tall **and** hold at least 5 credits.
Print `Sorry, you cannot ride.` or `Enjoy the ride!`.

```python
height = {{height}}
credits = {{credits}}
if height < 137 or credits < 5:
    print('Sorry, you cannot ride.')
else:
    print('Enjoy the ride!')
```
</instructions>

<help>
<hint>Failing either rule means no ride, so the condition for rejection uses `or`.</hint>
<solution>
height = {{height}}
credits = {{credits}}
if height < 137 or credits < 5:
    print('Sorry, you cannot ride.')
else:
    print('Enjoy the ride!')
</solution>
</help>
