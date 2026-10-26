---
order: 4
exercise: 20
title: Botol Soda
module: 4
check: strict
vars: |
  start = randint(3, 6)
expect: |
  {{[f'{n} bottle' + ('' if n == 1 else 's') + ' of pop on the wall' for n in range(start, 0, -1)]}}
---

<learn>
Loop juga bisa menghitung mundur. `range(start, 0, -1)` menghasilkan angka
menurun.

```python
for n in range(5, 0, -1):
    print(n)
```

Angka ketiga adalah langkahnya: `-1` berarti turun satu setiap putaran.
</learn>

<instructions>
Mulai dari **{{start}}** botol soda dan hitung mundur sampai 1, cetak satu
baris per hitungan:

```output
{{start}} bottles of pop on the wall
...
1 bottle of pop on the wall
```

Gunakan `bottles` untuk jumlahnya. Baris terakhir harus berbunyi **bottle**,
bukan bottles.
</instructions>

<help>
<hint>Loop mundur dari jumlah botol sampai 1. Perhatikan bentuk kata pada hitungan terakhir.</hint>
<solution>
bottles = {{start}}
while bottles > 0:
    if bottles == 1:
        print(f'{bottles} bottle of pop on the wall')
    else:
        print(f'{bottles} bottles of pop on the wall')
    bottles = bottles - 1
</solution>
</help>
