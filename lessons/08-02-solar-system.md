---
order: 2
exercise: 40
title: Tata Surya
module: 8
check: strict
vars: |
  planet = choice(['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter'])
  distance = {'Mercury': 57.9, 'Venus': 108.2, 'Earth': 149.6,
              'Mars': 227.9, 'Jupiter': 778.6}[planet]
expect: |
  {{planet}} is {{distance}} million km from the Sun.
---

<learn>
**Dictionary** menyimpan pasangan kunci dan nilai.

```python
jarak = {'Bumi': 149.6, 'Mars': 227.9}
print(jarak['Mars'])
```

Nilainya diambil dengan kunci di dalam tanda kurung siku.
</learn>

<instructions>
Dengan dictionary berisi jarak, cari **{{planet}}** dan cetak:

```output
{{planet}} is {{distance}} million km from the Sun.
```
</instructions>

<help>
<hint>Ambil nilai dari dictionary memakai nama planet sebagai kunci, lalu susun kalimatnya.</hint>
<solution>
distances = {'Mercury': 57.9, 'Venus': 108.2, 'Earth': 149.6,
             'Mars': 227.9, 'Jupiter': 778.6}
planet = '{{planet}}'
print(f'{planet} is {distances[planet]} million km from the Sun.')
</solution>
</help>
