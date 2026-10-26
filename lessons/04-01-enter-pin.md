---
order: 1
exercise: 17
title: Masukkan PIN
module: 4
check: strict
vars: |
  pin = randint(1000, 9999)
expect: |
  ACCESS GRANTED
---

<learn>
`while` mengulang blok kode selama kondisinya masih benar.

```python
guess = 0
while guess != pin:
    guess = guess + 1
```

Hati-hati: kalau kondisinya tidak pernah berubah menjadi salah, loop akan
berjalan selamanya.
</learn>

<instructions>
Tulis loop `while` yang terus menebak PIN sampai PIN yang benar, **{{pin}}**,
tercapai. Saat cocok, cetak `ACCESS GRANTED`.

Karena terminal ini tidak punya papan ketik, pakai penghitung sebagai ganti
`input()`: ulangi selama tebakan masih salah, lalu cetak pesannya.

```python
pin = {{pin}}
guess = 0
while guess != pin:
    guess = pin
print('ACCESS GRANTED')
```
</instructions>

<help>
<hint>Kondisi loop-nya `guess != pin`, dan di dalam loop nilainya diperbarui sampai cocok.</hint>
<solution>
pin = {{pin}}
guess = 0
while guess != pin:
    guess = pin
print('ACCESS GRANTED')
</solution>
</help>
