---
order: 1
exercise: 34
title: Restoran
module: 7
check: strict
vars: |
  name = choice(['Blue Door', 'Sakura', 'Corner Cafe', 'Little Italy'])
  cuisine = choice(['Italian', 'Japanese', 'French', 'Mexican'])
expect: |
  {{name}} serves {{cuisine}} food.
---

<learn>
Sebuah **class** adalah cetak biru untuk membuat objek.

```python
class Restaurant:
    def __init__(self, name, cuisine):
        self.name = name
        self.cuisine = cuisine
```

`__init__` dijalankan saat objek dibuat, dan `self` merujuk pada objek itu
sendiri.
</learn>

<instructions>
Buat class `Restaurant` yang `__init__`-nya menerima nama dan jenis masakan.

Lalu buat satu untuk **{{name}}**, yang menyajikan masakan **{{cuisine}}**,
dan cetak:

```output
{{name}} serves {{cuisine}} food.
```

```python
class Restaurant:
    def __init__(self, name, cuisine):
        self.name = name
        self.cuisine = cuisine

place = Restaurant('{{name}}', '{{cuisine}}')
print(f'{place.name} serves {place.cuisine} food.')
```
</instructions>

<help>
<hint>Simpan kedua argumen sebagai atribut `self`, lalu susun kalimatnya dengan f-string.</hint>
<solution>
class Restaurant:
    def __init__(self, name, cuisine):
        self.name = name
        self.cuisine = cuisine

place = Restaurant('{{name}}', '{{cuisine}}')
print(f'{place.name} serves {place.cuisine} food.')
</solution>
</help>
