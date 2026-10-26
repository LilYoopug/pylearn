---
order: 1
exercise: 22
title: Belanja
module: 5
check: strict
vars: |
  items = sample(['milk', 'bread', 'eggs', 'rice', 'apples', 'coffee'], 3)
expect: |
  {{items}}
---

<learn>
Sebuah **list** menyimpan banyak nilai dalam satu variabel, dan urutannya
dijaga.

```python
warna = ['merah', 'hijau', 'biru']
```

Kamu bisa menelusurinya dengan `for`, dan setiap putaran mengambil satu
elemen.
</learn>

<instructions>
Buat list berisi tepat tiga item ini, dengan urutan seperti ini:

{{items}}

Lalu cetak setiap item pada barisnya sendiri.

```python
shopping = {{items}}
for item in shopping:
    print(item)
```
</instructions>

<help>
<hint>Buat list dengan tiga string, lalu telusuri dengan `for` dan cetak satu per satu.</hint>
<solution>
shopping = {{items}}
for item in shopping:
    print(item)
</solution>
</help>
