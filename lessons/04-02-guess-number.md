---
order: 2
exercise: 18
title: Tebak Angka
module: 4
check: strict
vars: |
  secret = randint(1, 20)
  steps = 0
  guess = 0
  while guess != secret:
      guess = guess + 1
      steps = steps + 1
expect: "{{steps}}"
---

<learn>
Penghitung adalah pola yang sangat sering dipakai: mulai dari nol, tambah satu
setiap putaran.

```python
steps = 0
while guess != secret:
    guess = guess + 1
    steps = steps + 1
```

Di akhir loop, `steps` berisi berapa kali putaran yang sudah terjadi.
</learn>

<instructions>
Angka rahasianya adalah **{{secret}}**. Hitung berapa tebakan yang diperlukan
kalau kamu menebak 1, lalu 2, lalu 3, dan seterusnya sampai kena.

Cetak jumlah tebakannya.
</instructions>

<help>
<hint>Satu variabel untuk tebakan, satu untuk hitungan. Keduanya bertambah satu tiap putaran.</hint>
<solution>
secret = {{secret}}
steps = 0
guess = 0
while guess != secret:
    guess = guess + 1
    steps = steps + 1
print(steps)
</solution>
</help>
