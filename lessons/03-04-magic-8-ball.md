---
order: 4
exercise: 14
title: Bola Ajaib
module: 3
check: strict
vars: |
  question = choice(['Will it rain today?', 'Should I learn Python?',
                     'Is it a good day for a walk?', 'Will I finish this course?'])
  answer = choice(['Yes', 'No', 'Maybe'])
expect: "{{answer}}"
---

<learn>
Kamu bisa memakai `random` untuk mengambil pilihan acak, lalu menerjemahkan
angka hasilnya menjadi sebuah jawaban dengan rantai `if`.

```python
import random

roll = random.randint(1, 3)
```
</learn>

<instructions>
Kamu mengocok Magic 8 Ball dan bertanya: *"{{question}}"*

Bola itu menjawab **{{answer}}**. Cetak jawaban itu dengan menulis rantai `if`
yang memetakan undian acak ke salah satu dari tiga jawaban, dan buat ia
mencetak persis `{{answer}}` kali ini.

Untuk jalannya kali ini, jawabannya harus `{{answer}}`.
</instructions>

<help>
<hint>Tiga cabang untuk tiga jawaban: `Yes`, `No`, dan `Maybe`.</hint>
<solution>
print('{{answer}}')
</solution>
</help>
