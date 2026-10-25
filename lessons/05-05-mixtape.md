---
order: 5
exercise: 26
title: Playlist
xp: 25
module: 5
vars: |
  tracks = sample(['Blue Monday', 'Nights', 'Teardrop', 'Redbone',
                   'Borderline', 'Dreams'], 4)
expect: |
  {{[f'{i + 1}. {t}' for i, t in enumerate(tracks)]}}
---

<learn>
Putting a list together with a loop is one of the most common things you will
do. A **side** and a **track** belong together, so a tuple inside a list keeps
them paired:

```python
tape = [('A', 'Blue Monday'), ('B', 'Nights')]
for side, track in tape:
    print(side, track)
```

Python unpacks each pair into the two names for you.
</learn>

<instructions>
Make a mixtape from these tracks, in this order:

{{tracks}}

Print them as a numbered tracklist, one per line:

```output
{{[f'{i + 1}. {t}' for i, t in enumerate(tracks)]}}
```
</instructions>

<help>
<hint>A single list of titles is enough here. `enumerate(tape, start=1)` numbers them.</hint>
<solution>
tape = {{tracks}}
for number, track in enumerate(tape, start=1):
    print(f'{number}. {track}')
</solution>
</help>
