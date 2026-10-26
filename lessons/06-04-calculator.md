---
order: 4
exercise: 31
title: Kalkulator
module: 6
check: strict
vars: |
  a = randint(4, 20)
  b = randint(2, 9)
  total = a + b
expect: "{{total}}"
---

<learn>
Fungsi bisa menerima **argumen**, yaitu nilai yang kamu berikan saat
memanggilnya.

```python
def add(a, b):
    return a + b

print(add(2, 3))
```

`a` dan `b` disebut parameter; `2` dan `3` adalah argumen yang masuk ke sana.
</learn>

<instructions>
Tulis fungsi `add(a, b)` yang mengembalikan jumlah kedua argumennya.

Lalu jumlahkan **{{a}}** dan **{{b}}** memakai fungsi itu dan cetak hasilnya.
</instructions>

<help>
<hint>Fungsi menerima dua parameter dan mengembalikan `a + b`. Panggil dengan dua angka.</hint>
<solution>
def add(a, b):
    return a + b

print(add({{a}}, {{b}}))
</solution>
</help>
