---
order: 5
exercise: 26
title: Kaset Campuran
module: 5
check: strict
vars: |
  tracks = sample(['Blue Monday', 'Nights', 'Teardrop', 'Redbone',
                   'Borderline', 'Dreams'], 4)
expect: |
  {{[f'{i + 1}. {t}' for i, t in enumerate(tracks)]}}
---

<learn>
Kamu bisa menggabungkan `enumerate()` dengan f-string untuk membuat daftar
bernomor dalam satu baris.

```python
for i, lagu in enumerate(tracks):
    print(f'{i + 1}. {lagu}')
```
</learn>

<instructions>
Buat mixtape dari lagu-lagu ini, dengan urutan seperti ini:

{{tracks}}

Cetak sebagai daftar lagu bernomor, satu per baris:

```output
{{[f'{i + 1}. {t}' for i, t in enumerate(tracks)]}}
```
</instructions>

<help>
<hint>`enumerate()` memberi nomor, f-string menyusun teksnya. Ingat tambahkan 1 pada nomornya.</hint>
<solution>
tape = {{tracks}}
for number, track in enumerate(tape, start=1):
    print(f'{number}. {track}')
</solution>
</help>
