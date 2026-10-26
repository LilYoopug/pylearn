---
order: 4
exercise: 42
title: Empat Puluh Dua
module: 8
check: output
vars: |
  target = 42
expect: "{{float(target)}}"
---

<learn>
Modul `math` menyediakan fungsi matematika yang lebih lengkap, termasuk
`math.sqrt` untuk akar kuadrat.

```python
import math
print(math.sqrt(9))
```

Untuk memakainya, modulnya harus diimpor lebih dulu.
</learn>

<instructions>
Jawaban dari segala hal adalah **{{target}}**.

Gunakan `math.sqrt` untuk menghitung akar kuadrat yang hasilnya sama dengan
itu, lalu cetak hasilnya.
</instructions>

<help>
<hint>Akar kuadrat dari kuadrat sebuah angka menghasilkan angka itu sendiri.</hint>
<solution>
import math

print(math.sqrt({{target ** 2}}))
</solution>
</help>
