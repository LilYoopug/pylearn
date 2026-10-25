# Panduan format materi

Setiap level adalah satu file `.md` di dalam `lessons/`. Nama file mengikuti
pola `NN-slug.md` dan urutannya ditentukan oleh field `order`, bukan nama file.

```
lessons/
  01-01-hello-world.md
  01-02-print-statements.md
  01-03-variables.md
  02-01-booleans.md
```

## Frontmatter

Bagian paling atas adalah metadata level, ditulis sebagai `key: value`.

```markdown
---
order: 3
title: Variables
xp: 15
module: 1
---
```

| key        | wajib | arti                                            |
|------------|-------|-------------------------------------------------|
| `order`    | ya    | urutan level di dalam modulnya                  |
| `title`    | ya    | judul yang tampil di path, sidebar, dan header  |
| `xp`       | ya    | XP yang didapat saat level selesai              |
| `module`   | ya    | nomor modul tempat level ini berada             |
| `exercise` | tidak | nomor latihan global (default: `order`)         |
| `expect`   | tidak | stdout yang diharapkan, boleh berisi `{{...}}`  |
| `start`    | tidak | isi awal editor                                 |
| `vars`     | tidak | blok Python untuk nilai acak (lihat di bawah)   |

## Bagian

Isi materi dibagi oleh tag tingkat-atas. Semuanya opsional kecuali
`<instructions>`.

```markdown
<learn>
Teks bebas. Mendukung **bold**, *italic*, `inline code`, dan [tautan](url).
</learn>

<instructions>
Teks instruksi, boleh beberapa paragraf.
</instructions>

<help>
<hint>Petunjuk singkat.</hint>
<solution>
# Write code below 💖

print('Hi')
</solution>
</help>
```

### Blok yang tersedia di dalam `<learn>` dan `<instructions>`

| blok            | hasil                                                       |
|-----------------|-------------------------------------------------------------|
| paragraf biasa  | satu paragraf prose                                         |
| `- item`        | butir daftar dengan penanda                                |
| ` ```python `   | blok kode berwarna, dengan ikon salin                       |
| `<sprites/>`    | gambar pixel-art (lihat di bawah)                           |

### Blok kode

Blok kode berpagar ditampilkan sebagai kotak kode. Isinya diwarnai memakai
lexer Python yang sama dengan editor, jadi tidak perlu ditulis manual.

````markdown
```python
print('Hi')
```
````

Untuk blok kode *keluaran* (bukan kode yang dijalankan), pakai bahasa `output`:

````markdown
```output
Hi
```
````

### Sprite

```markdown
<sprites>snake,hero,skull</sprites>
```

Nama sprite yang tersedia didefinisikan di `pylearn.py` (`SPRITES`). Kalau
namanya tidak dikenal, blok itu dilewati tanpa error.

## Nilai acak dengan `vars`

Kalau jawaban selalu sama, murid bisa menghafalnya. Blok `vars` dijalankan
ulang **setiap kali level dibuka**, jadi soalnya berganti angka atau nama.

```markdown
---
order: 2
title: Temperature
xp: 15
module: 2
vars: |
  temp_f = randint(20, 110)
  temp_c = (temp_f - 32) / 1.8
expect: "{{temp_c}}"
---
```

Isinya Python biasa. Yang tersedia tanpa import:

| fungsi | contoh |
|--------|--------|
| `randint(a, b)` | `randint(1, 10)` |
| `choice(list)` | `choice(['Oslo', 'Lima'])` |
| `sample(list, n)` | `sample(items, 3)` |
| `uniform(a, b)` | `round(uniform(1.5, 2.0), 1)` |
| `round`, `abs`, `min`, `max`, `sum`, `len`, `sorted` | — |

Baris berikutnya boleh memakai nama dari baris sebelumnya, jadi nilai turunan
(seperti `total`) selalu konsisten dengan nilai acaknya.

## Menyisipkan nilai ke teks: `{{ ... }}`

Di dalam `<learn>`, `<instructions>`, `<hint>`, `<solution>`, dan `expect`,
`{{ ... }}` diganti dengan hasil ekspresi itu.

```markdown
The temperature today is **{{temp_f}}°F**.
```

Yang bisa ditulis di dalam kurung kurawal bukan hanya nama variabel, tapi
ekspresi Python apa pun:

```markdown
{{temp_f - 32}}
{{[f'{i + 1}. {t}' for i, t in enumerate(tracks)]}}
{{repr(items)}}
```

Bedanya per konteks:

- Di **teks** dan **`expect`**, sebuah list dicetak sebagai baris-baris
  (satu item per baris), karena itu yang biasanya dimaksud.
- Di **blok kode** dan **`solution`**, list tetap ditulis sebagai literal
  Python (`['a', 'b']`), karena di sana isinya kode.

Kalau ekspresinya gagal, teks aslinya dibiarkan apa adanya — jadi `{{` yang
tidak dimaksud tidak merusak apa pun.

## Jawaban yang diterima

Level menilai jawaban dari **stdout** program yang dijalankan, bukan dari
teks editor. Jadi beberapa solusi berbeda tetap diterima selama keluarannya
sama.

```markdown
---
order: 1
title: Hello World
xp: 10
module: 1
expect: Hi
---
```

| key      | arti                                                       |
|----------|------------------------------------------------------------|
| `expect` | stdout harus sama persis (setelah `strip()`). Opsional.     |
| `start`  | kode awal di editor. Opsional, default `# Write code below 💖` |

Kalau `expect` tidak diisi, level dianggap selesai asal program berjalan tanpa
error.

## Menambah level baru

1. Buat file baru di `lessons/` dengan pola `NN-slug.md`.
2. Isi frontmatter dan bagiannya.
3. Jalankan aplikasi — level otomatis muncul di modul yang sesuai.

Tidak ada daftar yang perlu diedit di kode.
