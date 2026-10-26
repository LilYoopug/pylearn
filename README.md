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
| `Tab` / `Enter` | Insert the highlighted completion |
| `↑` `↓` | Move through completions (while the popup is open) |
| `ctrl+space` | Open the completion list |

Everything is also clickable.

## IntelliSense

The editor completes from the code you are actually writing — no language
server, no extra dependency. Type a name and it appears in a popup under the
caret; type a dot and it lists the members of that value.

```
names = ['ada', 'guido']      ┌─────────────────────┐
total = len(names)            │ ▸ ≡ append          │
                              │   ≡ clear           │
names.█                       │   ≡ copy            │
                              │   ≡ count           │
                              └─────────────────────┘
```

What it knows about:

| Source | Example |
|--------|---------|
| Variables in the file | `total` → `int` |
| Functions, with their signature | `greet` → `(name, punct=…)` |
| Classes and their methods | `Dog` → `bark`, `fetch` |
| Members of a known value | `names.` → `append`, `sort`, … |
| Members after a literal | `"abc".` → `upper`, `split`, … |
| Python builtins | `print`, `range`, `len`, `sum` |
| Keywords | `for`, `while`, `import` |

| Key | Action |
|-----|--------|
| `Tab` / `Enter` | Insert the highlighted completion |
| `↑` `↓` | Move through the list |
| `Esc` | Close the popup |
| `ctrl+space` | Open the list manually |

The popup sizes itself to the space left around the caret: it opens below the
line, flips above when there is more room there, and shows as many rows as fit
instead of drawing a fixed block over the terminal. A counter (`1-5/11`) says
how many more there are, and the list scrolls with `↑` `↓`.

### Accepting a function writes the parentheses

Like `python.analysis.completeFunctionParens` in Pylance: accepting `print`
writes `print()` and puts the caret **between** the brackets, ready for
arguments.

```python
print(█)
```

Parentheses are deliberately **not** added inside an `import`, a type
annotation or a decorator — a call is not what is wanted there:

| you type | you get |
|----------|---------|
| `import pri` | `import print` |
| `x: pri` | `x: print` |
| `@pri` | `@print` |
| `print(pri` | `print(print())` |

### Signature help

Inside a call, the parameters are shown under the editor and the active one is
highlighted. It appears when you type `(`, advances on every `,`, and hides
when the caret leaves the call:

```
ƒ print(*values, sep, end)   ▸ sep  (2/3)
```

Signatures come from the functions defined in your file and from a table of
Python builtins, so `range(`, `sorted(` and `print(` all explain themselves.

The source is parsed with `ast`, so symbols are read exactly rather than
guessed with regexes. Code that is still being typed is handled: `names.` and
unclosed brackets are syntax errors, so the offending lines are dropped and
the rest of the file still contributes its names — a completion list that is
mostly right beats an empty one.

Types are inferred where the value makes it obvious (`x = []` → list,
`total = len(...)` → int). Anything else falls back to the static member table,
because resolving a return type without running the code is not possible.

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

Each lesson declares how it is judged with `check:` in its frontmatter:

| `check:` | meaning |
|----------|---------|
| `output` | stdout must equal `expect` (the default) |
| `strict` | the same, and the program must also exit cleanly |

`strict` stops a program that crashes halfway from counting as an answer.
A third mode, `reseed`, was tried and removed: it re-rolled the level and ran
the answer again to catch a copied number, but every lesson prints its values
on screen, so the reference solution itself is written with those literals and
was rejected by its own checker.

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
