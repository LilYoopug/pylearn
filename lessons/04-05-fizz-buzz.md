---
order: 5
exercise: 21
title: Fizz Buzz
module: 4
check: strict
vars: |
  limit = randint(5, 9)
expect: |
  {{[('FizzBuzz' if i % 15 == 0 else 'Fizz' if i % 3 == 0 else 'Buzz' if i % 5 == 0 else str(i)) for i in range(1, limit + 1)]}}
---

<learn>
Operator `%` (modulo) memberi sisa bagi. Kalau `n % 3 == 0`, berarti `n` habis
dibagi 3.

Ini cara klasik memeriksa kelipatan.
</learn>

<instructions>
Untuk setiap angka dari 1 sampai **{{limit}}**, cetak:

- `FizzBuzz` kalau habis dibagi 3 dan 5
- `Fizz` kalau habis dibagi 3
- `Buzz` kalau habis dibagi 5
- angka itu sendiri kalau tidak memenuhi semuanya
</instructions>

<help>
<hint>Periksa kelipatan 15 lebih dulu, baru 3, lalu 5 — urutannya menentukan hasil.</hint>
<solution>
for i in range(1, {{limit}} + 1):
    if i % 15 == 0:
        print('FizzBuzz')
    elif i % 3 == 0:
        print('Fizz')
    elif i % 5 == 0:
        print('Buzz')
    else:
        print(i)
</solution>
</help>
