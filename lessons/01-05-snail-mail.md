---
order: 5
exercise: 5
title: Alamat Amplop
module: 1
check: strict
vars: |
  name = choice(['Ada', 'Grace', 'Alan', 'Katherine', 'Linus', 'Margaret'])
  city = choice(['Oslo', 'Lima', 'Kyoto', 'Cairo', 'Lisbon', 'Nairobi'])
  street = choice(['Elm Street', 'Harbour Road', 'Sunset Boulevard', 'Kingsway'])
  number = randint(1, 240)
expect: |
  {{name}}
  {{number}} {{street}}
  {{city}}
---

<learn>
Sebuah surat punya bentuk: nama pada barisnya sendiri, lalu alamat jalan, lalu
kota. Tugasmu meniru bentuk itu dengan `print()`.

Inilah gunanya fungsi `print()` — satu pemanggilan untuk satu baris alamat.
</learn>

<instructions>
Cetak alamat amplop untuk **{{name}}**, yang tinggal di
**{{number}} {{street}}**, **{{city}}**.

Harus tepat tiga baris, dengan urutan ini:

```output
{{name}}
{{number}} {{street}}
{{city}}
```

Perhatikan bahwa nomor dan nama jalan berada di satu baris, dipisahkan satu
spasi.
</instructions>

<help>
<hint>Tiga pemanggilan `print()`. Baris tengah berisi dua nilai dalam satu string.</hint>
<solution>
print('{{name}}')
print('{{number}} {{street}}')
print('{{city}}')
</solution>
</help>
