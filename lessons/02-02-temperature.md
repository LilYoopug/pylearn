---
order: 2
exercise: 7
title: Suhu
module: 2
check: strict
vars: |
  temp_f = randint(20, 110)
  temp_c = (temp_f - 32) / 1.8
expect: "{{temp_c}}"
---

<learn>
Python dengan senang hati mengerjakan aritmetika untukmu — kamu hanya perlu
menulis rumusnya sekali.

Konversi Fahrenheit ke Celsius adalah:

```
celsius = (fahrenheit - 32) / 1.8
```

Taruh angkanya di variabel, tulis rumusnya dalam bentuk variabel itu, lalu
cetak hasilnya. Python mengerjakan sisanya.
</learn>

<instructions>
Suhu hari ini adalah **{{temp_f}}°F**. Konversikan ke Celsius dan cetak
hasilnya.

Jangan bulatkan jawabannya — cetak persis seperti yang dihitung Python.
</instructions>

<help>
<hint>Kurangi 32 dulu, baru bagi 1.8. Tanda kurung penting: tanpa itu Python membagi sebelum mengurangi.</hint>
<solution>
temp_f = {{temp_f}}
temp_c = (temp_f - 32) / 1.8
print(temp_c)
</solution>
</help>
