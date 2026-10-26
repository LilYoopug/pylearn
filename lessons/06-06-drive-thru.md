---
order: 6
exercise: 33
title: Pesan Makanan
module: 6
check: strict
vars: |
  item = choice(['burger', 'fries', 'shake', 'taco'])
  price = randint(3, 12)
  total = price * 2
expect: |
  You ordered {{item}}.
  Total: {{total}}
---

<learn>
Parameter bisa punya **nilai bawaan**, sehingga pemanggil boleh tidak
menyebutkannya.

```python
def order(item, quantity=1):
    ...
```

Kalau `quantity` tidak diberikan, nilainya 1.
</learn>

<instructions>
Tulis fungsi `order(item, quantity=1)` yang mengembalikan kalimat berisi
pesanan. Panggil untuk **2× {{item}}** lalu cetak:

```output
You ordered {{item}}.
Total: {{total}}
```

Setiap item berharga **{{price}}**.
</instructions>

<help>
<hint>Kalimat pertama menyebut nama item, baris kedua berisi total harga = harga × jumlah.</hint>
<solution>
def order(item, quantity=1):
    return f'You ordered {item}.'

print(order('{{item}}', 2))
print(f'Total: { {{price}} * 2 }')
</solution>
</help>
