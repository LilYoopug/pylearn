---
order: 6
exercise: 16
title: Topi Pemilah
module: 3
check: strict
vars: |
  score = randint(0, 100)
  if score >= 90:
      house = 'Gryffindor'
  elif score >= 75:
      house = 'Ravenclaw'
  elif score >= 60:
      house = 'Hufflepuff'
  else:
      house = 'Slytherin'
expect: "{{house}}"
---

<learn>
Saat ada lebih dari dua kemungkinan, `elif` membuat pemeriksaan berjalan
berurutan dari kondisi paling ketat.

Urutannya penting: kondisi pertama yang cocok yang dipakai, jadi mulailah
dari yang paling besar.
</learn>

<instructions>
Topi pemilah membaca sebuah skor **{{score}}**.

| skor        | asrama      |
|-------------|-------------|
| 90 ke atas  | Gryffindor  |
| 75 ke atas  | Ravenclaw   |
| 60 ke atas  | Hufflepuff  |
| di bawah 60 | Slytherin   |

Cetak nama asramanya saja.
</instructions>

<help>
<hint>Empat cabang berurutan, dimulai dari skor tertinggi.</hint>
<solution>
score = {{score}}
if score >= 90:
    house = 'Gryffindor'
elif score >= 75:
    house = 'Ravenclaw'
elif score >= 60:
    house = 'Hufflepuff'
else:
    house = 'Slytherin'
print(house)
</solution>
</help>
