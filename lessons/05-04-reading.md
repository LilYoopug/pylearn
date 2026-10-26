---
order: 4
exercise: 25
title: Daftar Bacaan
module: 5
check: strict
vars: |
  books = sample(['Dune', 'Emma', 'Beloved', 'Ulysses', 'Dracula', 'Middlemarch'], 3)
  target = books[1]
expect: "{{target}}"
---

<learn>
Elemen list bisa diambil lewat **indeks**, dan penghitungannya mulai dari 0.

```python
buku = ['Dune', 'Emma', 'Beloved']
print(buku[0])   # Dune
print(buku[1])   # Emma
```

Indeks negatif menghitung dari belakang: `buku[-1]` adalah elemen terakhir.
</learn>

<instructions>
Daftar bacaanmu berisi:

{{books}}

Cetak buku **kedua** pada daftar itu, memakai indeksnya bukan string yang
ditulis manual.
</instructions>

<help>
<hint>Buku kedua ada di indeks 1, karena indeks dimulai dari 0.</hint>
<solution>
books = {{books}}
print(books[1])
</solution>
</help>
