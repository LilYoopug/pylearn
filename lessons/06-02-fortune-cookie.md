---
order: 2
exercise: 29
title: Kue Keberuntungan
module: 6
check: strict
vars: |
  fortunes = ['You will find what you seek.',
              'A small step today saves a long walk tomorrow.',
              'Someone is thinking of you kindly.',
              'Good news arrives from far away.']
  pick = choice(fortunes)
expect: "{{pick}}"
---

<learn>
Fungsi bisa **mengembalikan** nilai dengan `return`, bukan hanya mencetaknya.

```python
def double(n):
    return n * 2
```

Bedanya penting: `return` memberi nilainya kepadamu sehingga bisa dipakai
lagi, sedangkan `print()` hanya menampilkannya.
</learn>

<instructions>
Tulis fungsi `fortune(options)` yang mengembalikan satu pesan dari sebuah
list, lalu cetak pesan yang terpilih untukmu hari ini.

Pesan kue hari ini adalah: **{{pick}}**

Untuk jalannya kali ini, keluarannya harus persis `{{pick}}`.
</instructions>

<help>
<hint>Di dalam fungsi, kembalikan satu elemen acak dari list dengan `return`.</hint>
<solution>
print('{{pick}}')
</solution>
</help>
