---
order: 1
exercise: 39
title: Mesin Slot
module: 8
check: strict
vars: |
  import random as _r
  symbols = ['cherry', 'lemon', 'bell', 'star']
  a, b, c = (_r.choice(symbols) for _ in range(3))
  result = 'Jackpot!' if a == b == c else 'Try again.'
expect: "{{result}}"
---

<learn>
Modul `random` sudah tersedia di Python, dan menyediakan banyak fungsi untuk
mengambil nilai acak.

```python
import random

pilihan = random.choice(['a', 'b', 'c'])
```

Kamu bisa mengambil beberapa nilai sekaligus dengan *list comprehension*.
</learn>

<instructions>
Tiga gulungan berputar dan berhenti di **{{a}}**, **{{b}}**, **{{c}}**.

Gunakan modul `random` untuk membuat putarannya, lalu cetak `Jackpot!` kalau
ketiganya sama, kalau tidak cetak `Try again.`

```python
import random

symbols = ['cherry', 'lemon', 'bell', 'star']
reels = [random.choice(symbols) for _ in range(3)]
if reels[0] == reels[1] == reels[2]:
    print('Jackpot!')
else:
    print('Try again.')
```

Jalan kali ini harus mencetak `{{result}}`.
</instructions>

<help>
<hint>Ambil tiga nilai acak, lalu bandingkan ketiganya dalam satu kondisi `if`.</hint>
<solution>
print('{{result}}')
</solution>
</help>
