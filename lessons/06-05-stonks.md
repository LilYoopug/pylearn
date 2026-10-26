---
order: 5
exercise: 32
title: Nilai Saham
module: 6
check: strict
vars: |
  price = randint(20, 300)
  shares = randint(2, 40)
  value = price * shares
expect: "{{value}}"
---

<learn>
Fungsi yang baik punya satu tugas yang jelas. Kalau sebuah perhitungan dipakai
di beberapa tempat, jadikan fungsi.

```python
def luas(panjang, lebar):
    return panjang * lebar
```
</learn>

<instructions>
Kamu memiliki **{{shares}}** saham dengan harga **{{price}}** per lembar.

Tulis fungsi `value(price, shares)` yang mengembalikan total nilainya, lalu
cetak angkanya.
</instructions>

<help>
<hint>Fungsi mengembalikan harga dikali jumlah lembar. Panggil dengan urutan parameter yang benar.</hint>
<solution>
def value(price, shares):
    return price * shares

print(value({{price}}, {{shares}}))
</solution>
</help>
