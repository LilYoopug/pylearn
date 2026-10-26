---
order: 5
exercise: 38
title: Indeks Monster
module: 7
check: strict
vars: |
  mons = sample(['Bulbasaur', 'Charmander', 'Squirtle', 'Pikachu', 'Eevee'], 2)
expect: |
  {{[f'{n + 1}. {m}' for n, m in enumerate(mons)]}}
---

<learn>
Method `__str__` menentukan bagaimana objek ditampilkan saat dicetak.

```python
def __str__(self):
    return self.name
```

Dengan method itu, `print(objek)` akan menampilkan nama, bukan alamat memori.
</learn>

<instructions>
Buat class `Pokemon` dengan `name` dan `__str__` yang mengembalikan nama itu.

Lalu buat entri untuk dua monster ini dan cetak indeks bernomor:

```output
{{[f'{n + 1}. {m}' for n, m in enumerate(mons)]}}
```
</instructions>

<help>
<hint>`__str__` cukup mengembalikan `self.name`. Untuk penomoran, pakai `enumerate(..., start=1)`.</hint>
<solution>
class Pokemon:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

mons = [Pokemon(name) for name in {{mons}}]
for number, mon in enumerate(mons, start=1):
    print(f'{number}. {mon}')
</solution>
</help>
