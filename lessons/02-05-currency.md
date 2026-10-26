---
order: 5
exercise: 10
title: Currency
module: 2
vars: |
  pesos = randint(100, 2000)
  soles = randint(100, 2000)
  reais = randint(100, 2000)
  total = pesos * 0.00025 + soles * 0.28 + reais * 0.21
expect: "{{total}}"
---

<learn>
Money conversion is just multiplication, once per currency, added together.

Each line below converts one currency into dollars:

```python
pesos_usd = pesos * 0.00025
soles_usd = soles * 0.28
reais_usd = reais * 0.21
```

You can keep them in separate variables, or combine them into one expression.
Either is correct — the important part is that each amount is multiplied by
its own rate before being added.
</learn>

<instructions>
You came home with leftover currency:

- **{{pesos}}** Mexican pesos (rate `0.00025`)
- **{{soles}}** Peruvian soles (rate `0.28`)
- **{{reais}}** Brazilian reais (rate `0.21`)

Print the total in US dollars.

```python
pesos = {{pesos}}
soles = {{soles}}
reais = {{reais}}
total = pesos * 0.00025 + soles * 0.28 + reais * 0.21
print(total)
```

Print the value without rounding.
</instructions>

<help>
<hint>Multiply each amount by its rate, then add the three results together.</hint>
<solution>
pesos = {{pesos}}
soles = {{soles}}
reais = {{reais}}
total = pesos * 0.00025 + soles * 0.28 + reais * 0.21
print(total)
</solution>
</help>
