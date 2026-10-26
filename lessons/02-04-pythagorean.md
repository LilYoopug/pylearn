---
order: 4
exercise: 9
title: Pythagoras
module: 2
check: strict
vars: |
  a = randint(3, 15)
  b = randint(3, 15)
  c = (a ** 2 + b ** 2) ** 0.5
expect: "{{c}}"
---

<learn>
Teorema Pythagoras: pada segitiga siku-siku, kuadrat sisi miring sama dengan
jumlah kuadrat kedua sisi lainnya.

```
c = (a ** 2 + b ** 2) ** 0.5
```

Akar kuadrat sama saja dengan pangkat `0.5`.
</learn>

<instructions>
Sebuah segitiga siku-siku memiliki sisi **a = {{a}}** dan **b = {{b}}**. Cetak
panjang sisi miring `c`.

Cetak nilainya tanpa pembulatan.
</instructions>

<help>
<hint>Kuadratkan kedua sisi, jumlahkan, lalu ambil akarnya dengan `** 0.5`.</hint>
<solution>
a = {{a}}
b = {{b}}
c = (a ** 2 + b ** 2) ** 0.5
print(c)
</solution>
</help>
