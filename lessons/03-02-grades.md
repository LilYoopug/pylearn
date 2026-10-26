---
order: 2
exercise: 12
title: Nilai Siswa
module: 3
check: strict
vars: |
  grade = randint(30, 100)
  result = 'You passed.' if grade >= 55 else 'You failed.'
expect: "{{result}}"
---

<learn>
Kamu bisa membandingkan angka dengan `>=`, `<=`, `>` dan `<`.

```python
if score >= 55:
    print('Lulus')
```

`elif` dipakai saat ada lebih dari dua kemungkinan.
</learn>

<instructions>
Seorang siswa mendapat nilai **{{grade}}** dari 100. Batas kelulusan adalah
**55**.

Cetak `You passed.` atau `You failed.` sesuai kondisinya.
</instructions>

<help>
<hint>Gunakan satu perbandingan saja: kalau nilainya 55 atau lebih, cetak pesan lulus; sisanya gagal.</hint>
<solution>
grade = {{grade}}
if grade >= 55:
    print('You passed.')
else:
    print('You failed.')
</solution>
</help>
