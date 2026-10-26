---
order: 3
exercise: 30
title: Orbiter Mars
module: 6
check: strict
vars: |
  days = randint(30, 400)
  hours = days * 24
  minutes = hours * 60
expect: |
  Days: {{days}}
  Hours: {{hours}}
  Minutes: {{minutes}}
---

<learn>
Satu fungsi bisa dipakai berkali-kali dengan nilai berbeda — itu inti dari
manfaatnya.

Kalau sebuah nilai bisa dihitung dari nilai lain, hitung saja di dalam kode
daripada menulisnya manual.
</learn>

<instructions>
Wahana itu sudah terbang selama **{{days}}** hari.

Tulis fungsi `convert(days)` yang mengembalikan jumlah jam, lalu cetak ketiga
nilainya:

```output
Days: {{days}}
Hours: {{hours}}
Minutes: {{minutes}}
```

Gunakan fungsinya untuk jam; menit diturunkan dari jam.
</instructions>

<help>
<hint>Kalikan hari dengan 24 untuk jam, lalu jam dengan 60 untuk menit.</hint>
<solution>
def convert(days):
    return days * 24

days = {{days}}
hours = convert(days)
print(f'Days: {days}')
print(f'Hours: {hours}')
print(f'Minutes: {hours * 60}')
</solution>
</help>
