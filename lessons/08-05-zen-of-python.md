---
order: 5
exercise: 43
title: Zen Python
module: 8
check: output
vars: |
  count = 3
expect: |
  Beautiful is better than ugly.
  Explicit is better than implicit.
  Simple is better than complex.
---

<learn>
Python punya puisi singkat berisi prinsip desainnya, bernama *The Zen of
Python*.

Kamu bisa melihatnya sendiri dengan menjalankan `import this` di Python.
</learn>

<instructions>
Cetak **{{count}}** baris pertama Zen of Python, satu per baris:

```output
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
```
</instructions>

<help>
<hint>Tiga pemanggilan `print()`, satu untuk tiap baris, persis seperti contoh.</hint>
<solution>
print('Beautiful is better than ugly.')
print('Explicit is better than implicit.')
print('Simple is better than complex.')
</solution>
</help>
