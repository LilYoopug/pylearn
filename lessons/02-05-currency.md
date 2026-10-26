---
order: 5
exercise: 10
title: Mata Uang
module: 2
check: strict
vars: |
  pesos = randint(100, 2000)
  soles = randint(100, 2000)
  reais = randint(100, 2000)
  total = pesos * 0.00025 + soles * 0.28 + reais * 0.21
expect: "{{total}}"
---

<learn>
Kamu bisa menyimpan beberapa nilai sekaligus, lalu menjumlahkannya dalam satu
ekspresi.

Pastikan setiap nilai dikalikan dengan kursnya **sebelum** dijumlahkan.
</learn>

<instructions>
Kamu pulang membawa sisa mata uang:

- **{{pesos}}** peso Meksiko (kurs `0.00025`)
- **{{soles}}** sol Peru (kurs `0.28`)
- **{{reais}}** real Brasil (kurs `0.21`)

Cetak totalnya dalam dolar AS.

Cetak nilainya tanpa pembulatan.
</instructions>

<help>
<hint>Kalikan tiap jumlah dengan kursnya, lalu jumlahkan ketiga hasilnya.</hint>
<solution>
pesos = {{pesos}}
soles = {{soles}}
reais = {{reais}}
total = pesos * 0.00025 + soles * 0.28 + reais * 0.21
print(total)
</solution>
</help>
