---
order: 4
exercise: 4
title: Inisial
module: 1
check: output
expect: |
  AAAAA
  A   A
  AAAAA
  A   A
  A   A
---

<learn>
Karena spasi dihitung sebagai karakter, kamu bisa memakai `print()` untuk
menggambar huruf dan bentuk.

Tidak ada trik khusus: yang kamu perlukan hanya beberapa baris teks dengan
jumlah spasi yang tepat di dalam tanda kutip.
</learn>

<instructions>
Gambar huruf **A** hanya dengan karakter `A`, tinggi lima baris dan lebar
lima karakter:

```output
AAAAA
A   A
AAAAA
A   A
A   A
```

Pakai satu `print()` per baris, dan pertahankan spasi di dalam tanda kutip.
</instructions>

<help>
<hint>Baris kedua dan keempat hanya berisi dua huruf A dengan tiga spasi di antaranya.</hint>
<solution>
print('AAAAA')
print('A   A')
print('AAAAA')
print('A   A')
print('A   A')
</solution>
</help>
