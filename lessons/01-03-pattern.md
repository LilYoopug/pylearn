---
order: 3
exercise: 3
title: Pola Angka
module: 1
check: output
expect: |
          1
        2 3
      4 5 6
    7 8 9 10
---

<learn>
Setiap pemanggilan `print()` diakhiri baris baru. Jadi rangkaian `print()`
menggambar rangkaian baris — artinya kamu bisa menggambar dengan teks.

Kunci sebuah pola ada pada **spasi di dalam string**. `'  4 5 6'` bukan
string yang sama dengan `'4 5 6'`: yang pertama mulai tiga kolom lebih ke
kanan.
</learn>

<instructions>
Cetak segitiga angka ini, tepat empat baris, dengan spasi seperti yang
ditunjukkan:

```output
      1
    2 3
  4 5 6
7 8 9 10
```

Setiap baris mulai satu spasi lebih ke kiri daripada baris di atasnya.
</instructions>

<help>
<hint>Empat pemanggilan `print()`, satu per baris. Taruh spasi di awal string, sebelum angka pertama.</hint>
<solution>
print('      1')
print('    2 3')
print('  4 5 6')
print('7 8 9 10')
</solution>
</help>
