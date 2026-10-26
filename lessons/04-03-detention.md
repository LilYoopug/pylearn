---
order: 3
exercise: 19
title: Hukuman
module: 4
check: strict
vars: |
  lines = randint(3, 7)
expect: |
  {{["I will not talk in class."] * lines}}
---

<learn>
`for` mengulang sejumlah kali yang sudah diketahui.

```python
for i in range(3):
    print('halo')
```

`range(n)` menghasilkan angka `0` sampai `n - 1`, jadi blok di atas berjalan
tiga kali.
</learn>

<instructions>
Tulis baris `I will not talk in class.` tepat **{{lines}}** kali, satu per
baris.
</instructions>

<help>
<hint>Gunakan `range()` dengan jumlah baris yang diminta, lalu cetak kalimatnya di dalam loop.</hint>
<solution>
for i in range({{lines}}):
    print('I will not talk in class.')
</solution>
</help>
