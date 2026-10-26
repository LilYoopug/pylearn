---
order: 6
exercise: 27
title: Daftar Keinginan
module: 5
check: strict
vars: |
  dreams = sample(['see the northern lights', 'learn to sail',
                   'run a marathon', 'visit Japan', 'write a book'], 3)
expect: |
  {{[d.upper() for d in dreams]}}
---

<learn>
String punya banyak method bawaan, dan salah satunya adalah `upper()` yang
mengubah teks menjadi huruf kapital.

```python
print('halo'.upper())
```

Method dipanggil dengan titik setelah nilainya.
</learn>

<instructions>
Daftar keinginanmu:

{{dreams}}

Cetak setiap entri dalam **huruf kapital**, satu per baris.
</instructions>

<help>
<hint>Telusuri list-nya, lalu panggil `.upper()` pada setiap elemen sebelum dicetak.</hint>
<solution>
dreams = {{dreams}}
for dream in dreams:
    print(dream.upper())
</solution>
</help>
