---
order: 1
exercise: 6
title: Tipe Data
module: 2
check: strict
vars: |
  a = randint(2, 12)
  b = randint(2, 12)
  total = a + b
expect: "{{total}}"
---

<learn>
Sebuah **variabel** adalah nama untuk sebuah nilai:

```python
age = 42
```

Setiap nilai punya **tipe**. Empat tipe yang pertama kamu temui:

| tipe    | contoh    | arti                  |
|---------|-----------|-----------------------|
| `int`   | `7`       | bilangan bulat        |
| `float` | `7.5`     | bilangan berdesimal   |
| `str`   | `'seven'` | teks                  |
| `bool`  | `True`    | benar atau salah      |

Setelah sebuah nilai tersimpan di variabel, kamu bisa melakukan aritmetika
dengannya:

```python
a = 3
b = 4
print(a + b)
```

Operatornya adalah `+`, `-`, `*`, `/`, `**` (pangkat), dan `%` (sisa bagi).
</learn>

<instructions>
Simpan **{{a}}** di sebuah variabel dan **{{b}}** di variabel lain, lalu cetak
**jumlahnya**.

```python
a = {{a}}
b = {{b}}
print(a + b)
```

Terminal harus menampilkan satu angka.
</instructions>

<help>
<hint>Buat dua variabel, lalu cetak ekspresi `a + b` — jangan jumlahkan angkanya sendiri.</hint>
<solution>
a = {{a}}
b = {{b}}
print(a + b)
</solution>
</help>
