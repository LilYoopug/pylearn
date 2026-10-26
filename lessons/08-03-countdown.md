---
order: 3
exercise: 41
title: Hitung Mundur
module: 8
check: strict
vars: |
  start = randint(3, 7)
expect: |
  {{list(range(start, 0, -1))}}
  Liftoff!
---

<learn>
Modul dan fungsi bawaan Python membuat banyak hal menjadi singkat.

`range(start, 0, -1)` menghasilkan angka menurun, dan bisa langsung dipakai
di dalam loop.
</learn>

<instructions>
Hitung mundur dari **{{start}}** sampai 1, satu angka per baris, lalu cetak
`Liftoff!`.

```output
{{list(range(start, 0, -1))}}
Liftoff!
```
</instructions>

<help>
<hint>Loop dengan `range(start, 0, -1)` untuk angkanya, lalu cetak `Liftoff!` setelah loop selesai.</hint>
<solution>
for n in range({{start}}, 0, -1):
    print(n)
print('Liftoff!')
</solution>
</help>
