---
order: 5
exercise: 15
title: Wahana Cyclone
module: 3
check: strict
vars: |
  height = randint(120, 200)
  credits = randint(0, 10)
  if height < 137 or credits < 5:
      result = 'Sorry, you cannot ride.'
  else:
      result = 'Enjoy the ride!'
expect: "{{result}}"
---

<learn>
Operator logika menggabungkan beberapa perbandingan:

- `and` — benar hanya kalau **keduanya** benar
- `or` — benar kalau **salah satu** benar
- `not` — membalik hasilnya
</learn>

<instructions>
Seorang pengunjung setinggi **{{height}} cm** dan memiliki **{{credits}}**
kredit wahana.

Untuk bisa naik, tinggi minimal 137 cm **dan** kredit minimal 5. Cetak
`Sorry, you cannot ride.` atau `Enjoy the ride!`.
</instructions>

<help>
<hint>Cukup periksa kebalikannya: kalau tinggi kurang dari 137 **atau** kredit kurang dari 5, tolak.</hint>
<solution>
height = {{height}}
credits = {{credits}}
if height < 137 or credits < 5:
    print('Sorry, you cannot ride.')
else:
    print('Enjoy the ride!')
</solution>
</help>
