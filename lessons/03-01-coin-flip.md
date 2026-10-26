---
order: 1
exercise: 11
title: Lempar Koin
module: 3
check: strict
vars: |
  guess = choice(['Heads', 'Tails'])
  flip = choice(['Heads', 'Tails'])
  result = 'You win!' if guess == flip else 'You lose!'
expect: "{{result}}"
---

<learn>
`if` membuat program bisa memilih. Di dalamnya kamu menaruh sebuah
perbandingan, dan blok di bawahnya hanya dijalankan kalau perbandingan itu
**benar**.

```python
if guess == flip:
    print('You win!')
else:
    print('You lose!')
```

Perhatikan `==` (sama dengan) berbeda dari `=` (menyimpan nilai).
</learn>

<instructions>
Sebuah koin dilempar dan mendarat di **{{flip}}**. Tebakanmu **{{guess}}**.

Cetak `You win!` kalau tebakan cocok, kalau tidak cetak `You lose!`.

```python
guess = '{{guess}}'
flip = '{{flip}}'
if guess == flip:
    print('You win!')
else:
    print('You lose!')
```
</instructions>

<help>
<hint>Bandingkan kedua nilai dengan `==`, lalu cetak pesan yang sesuai di dalam blok `if` dan `else`.</hint>
<solution>
guess = '{{guess}}'
flip = '{{flip}}'
if guess == flip:
    print('You win!')
else:
    print('You lose!')
</solution>
</help>
