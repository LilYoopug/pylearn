---
order: 3
exercise: 36
title: Kota Favorit
module: 7
check: strict
vars: |
  cities = sample(['Tokyo', 'Lisbon', 'Cairo', 'Oslo', 'Quito', 'Perth'], 3)
expect: |
  {{cities}}
---

<learn>
Kamu bisa membuat banyak objek dari satu class, lalu menyimpannya dalam list.

```python
places = [City(name) for name in ['Oslo', 'Lima']]
```

Ini disebut *list comprehension*: cara ringkas membuat list dari perulangan.
</learn>

<instructions>
Buat class `City` yang menyimpan `name`, lalu bangun list berisi tiga kota ini:

{{cities}}

Cetak setiap nama pada barisnya sendiri.
</instructions>

<help>
<hint>Buat list berisi objek `City`, lalu telusuri dan cetak `.name` masing-masing.</hint>
<solution>
class City:
    def __init__(self, name):
        self.name = name

places = [City(name) for name in {{cities}}]
for place in places:
    print(place.name)
</solution>
</help>
