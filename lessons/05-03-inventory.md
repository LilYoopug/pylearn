---
order: 3
exercise: 24
title: Isi Tas
module: 5
check: strict
vars: |
  items = sample(['sword', 'shield', 'potion', 'rope', 'torch', 'map'], 4)
  count = len(items)
expect: |
  {{repr(items)}}
  Total items: {{count}}
---

<learn>
Fungsi `len()` mengembalikan jumlah elemen dalam sebuah list.

```python
items = ['pedang', 'peta']
print(len(items))
```

Kalau kamu mencetak list-nya langsung, Python menampilkan tanda kurung siku
dan tanda kutipnya.
</learn>

<instructions>
Kamu membawa empat item ini, dengan urutan seperti ini:

{{items}}

Cetak list-nya, lalu baris kedua berisi jumlah totalnya.

```output
{{repr(items)}}
Total items: {{count}}
```

Gunakan `len()` untuk jumlahnya — jangan tulis angkanya sendiri.
</instructions>

<help>
<hint>Cetak list-nya langsung, lalu cetak `len()` dari list itu di baris kedua.</hint>
<solution>
inventory = {{items}}
print(inventory)
print(f'Total items: {len(inventory)}')
</solution>
</help>
