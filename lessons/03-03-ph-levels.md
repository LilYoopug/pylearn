---
order: 3
exercise: 13
title: Tingkat pH
module: 3
check: strict
vars: |
  ph = randint(0, 14)
  if ph < 7:
      kind = 'Acidic'
  elif ph == 7:
      kind = 'Neutral'
  else:
      kind = 'Basic'
  result = f'pH {ph} is {kind}'
expect: "{{result}}"
---

<learn>
Rangkaian `if` / `elif` / `else` memeriksa kondisi secara berurutan, dan
hanya blok pertama yang cocok yang dijalankan.

Ini berguna saat sebuah nilai punya beberapa rentang, seperti tingkat
keasaman.
</learn>

<instructions>
Sebuah larutan memiliki pH **{{ph}}**. Cetak klasifikasinya dengan format
persis seperti ini:

```output
{{result}}
```

- di bawah 7 → `Acidic`
- tepat 7 → `Neutral`
- di atas 7 → `Basic`
</instructions>

<help>
<hint>Tiga cabang: satu untuk kurang dari 7, satu untuk tepat 7, satu lagi untuk sisanya.</hint>
<solution>
ph = {{ph}}
if ph < 7:
    kind = 'Acidic'
elif ph == 7:
    kind = 'Neutral'
else:
    kind = 'Basic'
print(f'pH {ph} is {kind}')
</solution>
</help>
