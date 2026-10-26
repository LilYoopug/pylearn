---
order: 2
exercise: 35
title: Papan Menu
module: 7
check: strict
vars: |
  item = choice(['burger', 'fries', 'shake'])
  price = randint(4, 15)
expect: |
  {{item}}: ${{price}}
---

<learn>
Selain atribut, class bisa punya **method** — fungsi yang menempel pada objek.

```python
class Menu:
    def label(self):
        return f'{self.item}: ${self.price}'
```

Method selalu menerima `self` sebagai parameter pertama.
</learn>

<instructions>
Tulis class `Menu` dengan `__init__(self, item, price)` dan method
`label(self)` yang mengembalikan `"{item}: ${price}"`.

Buat satu entri untuk **{{item}}** seharga **{{price}}** dolar dan cetak
label-nya.
</instructions>

<help>
<hint>Method `label` mengembalikan f-string dari kedua atribut. Panggil `label()` setelah objek dibuat.</hint>
<solution>
class Menu:
    def __init__(self, item, price):
        self.item = item
        self.price = price

    def label(self):
        return f'{self.item}: ${self.price}'

print(Menu('{{item}}', {{price}}).label())
</solution>
</help>
