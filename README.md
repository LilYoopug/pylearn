# pylearn

A terminal course for learning Python — a TUI you actually want to sit in front of.

`pylearn` is a single-file Textual app with 43 exercises across 8 modules. You
read the lesson on the left, write and run real Python on the right, and get
confetti when it works.

```
┌─ pylearn ─────────────────────────────────────────────────────────┐
│ ● pylearn   Python / First Steps / Hello World  ▐███▌ 7%  ⌂ ⚙ │
├───────────────────────────────┬───────────────────────────────────┤
│ Learn                         │ script.py                         │
│                               │                                   │
│ The programming language we   │ 1  # Write code below 💖          │
│ are learning is called Python │ 2                                 │
│ ...                           │ 3  print('Hi')                    │
│                               │                                   │
│ Instructions                  │        ⋯    ▶ Run   Submit answer │
│ Print exactly the word Hi.    │                                   │
│                               │ Terminal                          │
│ Help                          │ $ python script.py                │
│ ♡ Hint   · 3 more to unlock   │ Hi                                │
└───────────────────────────────┴───────────────────────────────────┘
```

## Why

Most "learn Python" terminals are a list of prompts. This one is a course: it
has a menu, a level map, gated hints, a real code editor with syntax colouring,
and it runs your code in a subprocess and checks the output.

## Install

Needs Python 3.11+.

```bash
pip install textual pygments
python pylearn.py
```

`rich` comes with Textual, so it is not listed separately.

> **Do not install `textual[syntax]`.** This app deliberately uses Pygments
> instead of tree-sitter: the `tree-sitter-python` binding fails to load on
> Termux (`cannot locate symbol ... external_scanner_create`), and Textual
> raises at construction time when the language is missing.

## Usage

| Key | Action |
|-----|--------|
| `ctrl+r` / `F5` | Run the code |
| `ctrl+s` | Submit the answer |
| `ctrl+q` | Quit |
| `↑` `↓` | Move through the level list |
| `Enter` | Open a level / start |
| `Esc` | Back one screen, close a popup |

Everything is also clickable.

The app opens on a menu, `Start` takes you to the level map, and `Home` walks
back up one screen at a time. `⚙ Setup` holds the accent colour, the menu
animation toggle and the confetti density.

## Course

| # | Module | Exercises |
|---|--------|-----------|
| 1 | First Steps | 1–5 |
| 2 | Values & Maths | 6–10 |
| 3 | Decisions | 11–16 |
| 4 | Repetition | 17–21 |
| 5 | Collections | 22–27 |
| 6 | Functions | 28–33 |
| 7 | Objects | 34–38 |
| 8 | Batteries | 39–43 |

Each level is a Markdown file in `lessons/`. Adding one is enough to make it
appear in the app — there is no list to edit in code.

## Writing a level

```markdown
---
order: 2
title: Temperature
module: 2
vars: |
  temp_f = randint(20, 110)
  temp_c = (temp_f - 32) / 1.8
expect: "{{temp_c}}"
---

<learn>
Fahrenheit to Celsius is `(f - 32) / 1.8`.
</learn>

<instructions>
The temperature is **{{temp_f}}°F**. Print it in Celsius.
</instructions>

<help>
<hint>Subtract 32 first, then divide by 1.8.</hint>
<solution>
temp_f = {{temp_f}}
print((temp_f - 32) / 1.8)
</solution>
</help>
```

The `vars` block is plain Python and runs again **every time the level is
opened**, so the numbers change and the answer cannot be memorised. `{{ ... }}`
in the text accepts any expression, not just a name.

Full format reference: [`lessons/README.md`](lessons/README.md).

## How the checking works

A level is judged by the **stdout** of your program, not by its source. That
means any correct implementation passes:

```bash
print('Hi')          # ✓
print("Hi")          # ✓
greeting = 'Hi'
print(greeting)      # ✓
```

Wrong answers put a red line in the Terminal and leave the level unfinished.
Hint unlocks after 3 wrong submissions, Solution after 6.

## Layout

```
pylearn.py            the whole app — UI, lesson loader call, confetti engine
lessons/
  __init__.py         Markdown + frontmatter loader
  README.md           lesson file format
  *.md                43 exercises
```

`pylearn.py` is deliberately a single file. The confetti particle system, the
beach menu scene and the code editor all live in it, so there is nothing to
install beyond the two packages above.

## Known limitations

- **Progress lives in one file.** Level states and hint counters are written to
  `pylearn_progress.json` next to `pylearn.py`; delete it (or use *Setup → Reset
  progress*) to start over.
- **No user input at runtime.** `input()` will not work, because the code runs
  in a subprocess with no keyboard attached. Exercises are written around this.
- **Accent colour is partial.** Textual cannot re-evaluate CSS variables at
  runtime, so changing the accent restyles the header and progress bar rather
  than the whole theme.

## Credits

The physics in the confetti overlay is a port of
[canvas-confetti](https://github.com/catdad/canvas-confetti) v1.9.3. The course
structure follows the shape of a beginner Python curriculum, but the lesson
text, examples and exercises here are written for this project.

## Licence

MIT.
