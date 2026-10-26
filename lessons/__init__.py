"""Loader for the lesson files in `lessons/`.

Each exercise is one Markdown file with a small frontmatter block and a few
XML-ish section tags. This module turns those files into plain dataclasses;
nothing here knows about Textual, so it can be tested on its own.

    from lessons import load_course
    course = load_course("lessons")
    course[0].levels[0].title   # "Setting Up"

The format is documented in `lessons/README.md`.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------- #
#  Data model
# --------------------------------------------------------------------------- #


@dataclass
class Block:
    """One piece of a lesson body: a paragraph, bullet, code box or sprite."""

    kind: str                 # "p" | "li" | "code" | "out" | "sprites"
    text: str = ""
    lang: str = ""


@dataclass
class Level:
    order: int
    exercise: int
    title: str
    module: int
    slug: str
    learn: list[Block] = field(default_factory=list)
    instructions: list[Block] = field(default_factory=list)
    hint: str = ""
    solution: str = ""
    expect: str | None = None
    start: str = "# Write code below 💖\n\n"

    check: str = "output"
    """How this level is judged: `output`, `reseed` or `strict`."""

    _vars_src: str = ""
    """Raw `<vars>` body, executed on every roll()."""

    _raw: dict = field(default_factory=dict)
    """Templates captured at parse time, substituted on every roll()."""

    vars: dict = field(default_factory=dict)
    """Current randomised values, available to templates as {{name}}."""

    def roll(self, seed: int | None = None) -> None:
        """Draw new random values and re-render every template.

        Called when the level is opened, so a replay gets fresh numbers and
        the learner cannot memorise one fixed answer.
        """
        self.vars = _run_vars(self._vars_src, seed)
        self.learn = [_render_block(b, self.vars) for b in self._raw["learn"]]
        self.instructions = [
            _render_block(b, self.vars) for b in self._raw["instructions"]
        ]
        self.hint = _fill(self._raw["hint"], self.vars)
        # the solution is Python, so lists stay literals
        self.solution = _fill(self._raw["solution"], self.vars, literal=True)
        self.expect = _fill(self._raw["expect"], self.vars) or None


@dataclass
class CourseModule:
    number: int
    title: str
    blurb: str
    levels: list[Level] = field(default_factory=list)


# --------------------------------------------------------------------------- #
#  Parsing
# --------------------------------------------------------------------------- #

_FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
_SECTION = re.compile(r"<(learn|instructions|help|vars)>(.*?)</\1>", re.S)
_TAG = re.compile(r"<(hint|solution)>(.*?)</\1>", re.S)
_VAR_REF = re.compile(r"\{\{(.+?)\}\}", re.S)


def _parse_front(text: str) -> dict[str, str]:
    """Parse `key: value` lines, including `key: |` block scalars."""
    meta: dict[str, str] = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        index += 1
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key, value = key.strip().lower(), value.strip()
        if value == "|":
            # block scalar: every following line indented deeper belongs here
            body: list[str] = []
            while index < len(lines):
                nxt = lines[index]
                if nxt.strip() and not nxt.startswith((" ", "\t")):
                    break
                body.append(nxt)
                index += 1
            while body and not body[0].strip():
                body.pop(0)
            while body and not body[-1].strip():
                body.pop()
            indent = min(
                (len(l) - len(l.lstrip()) for l in body if l.strip()), default=0
            )
            meta[key] = "\n".join(l[indent:] for l in body)
        else:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            meta[key] = value
    return meta


def _blocks(body: str) -> list[Block]:
    """Turn a section body into displayable blocks.

    Fenced code is pulled out first so its contents are never mistaken for
    prose or list items.
    """
    blocks: list[Block] = []
    # Only the outer newlines may go: `body.strip()` would also eat the
    # indentation that carries meaning inside an ```output block, which is how
    # a pattern like "   2 3" keeps its leading spaces.
    body = body.strip("\n")
    if not body.strip():
        return blocks

    parts: list[tuple[str, str, str]] = []
    cursor = 0
    pattern = re.compile(r"```(\w*)\n(.*?)```|<sprites>(.*?)</sprites>", re.S)
    for match in pattern.finditer(body):
        if match.start() > cursor:
            parts.append(("prose", "", body[cursor:match.start()]))
        if match.group(3) is not None:
            parts.append(("sprites", "", match.group(3)))
        else:
            parts.append(("code", match.group(1) or "python", match.group(2)))
        cursor = match.end()
    if cursor < len(body):
        parts.append(("prose", "", body[cursor:]))

    for kind, lang, payload in parts:
        if kind == "sprites":
            blocks.append(Block("sprites", payload.strip()))
            continue
        if kind == "code":
            # The fence's contents are indented to wherever the ``` sits.
            # Remove that common margin only — the spacing inside the sample
            # is the whole point of an output block.
            lines = payload.rstrip("\n").split("\n")
            margin = min((len(l) - len(l.lstrip()) for l in lines if l.strip()),
                         default=0)
            text = "\n".join(l[margin:] for l in lines)
            blocks.append(
                Block("out" if lang == "output" else "code", text, lang)
            )
            continue
        for chunk in re.split(r"\n\s*\n", payload):
            chunk = chunk.strip()
            if not chunk:
                continue
            lines = chunk.splitlines()
            if all(line.lstrip().startswith(("- ", "* ")) for line in lines):
                for line in lines:
                    blocks.append(Block("li", line.lstrip()[2:].strip()))
            elif _is_table(lines):
                blocks.append(_table_block(lines))
            else:
                blocks.append(Block("p", " ".join(l.strip() for l in lines)))
    return blocks


def _dedent(text: str) -> str:
    """Strip the common leading indent so solutions keep their own layout."""
    lines = text.strip("\n").splitlines()
    if not lines:
        return ""
    indents = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    cut = min(indents) if indents else 0
    return "\n".join(l[cut:] for l in lines).strip("\n")


def parse_level(path: Path) -> Level:
    raw = path.read_text(encoding="utf-8")
    front = _FRONT.search(raw)
    if front is None:
        raise ValueError(f"{path.name}: missing --- frontmatter ---")
    meta = _parse_front(front.group(1))
    body = raw[front.end():]

    for key in ("order", "title", "module"):
        if key not in meta:
            raise ValueError(f"{path.name}: frontmatter is missing '{key}'")

    learn: list[Block] = []
    instructions: list[Block] = []
    hint = solution = ""
    vars_src = ""

    vars_src = meta.get("vars", "")

    for name, section in _SECTION.findall(body):
        if name == "learn":
            learn = _blocks(section)
        elif name == "instructions":
            instructions = _blocks(section)
        elif name == "vars":
            vars_src = _dedent(section)
        else:
            tags = dict(_TAG.findall(section))
            hint = tags.get("hint", "").strip()
            solution = _dedent(tags.get("solution", ""))

    level = Level(
        order=int(meta["order"]),
        exercise=int(meta.get("exercise", meta["order"])),
        title=meta["title"],
        module=int(meta["module"]),
        slug=path.stem,
        start=meta.get("start", "# Write code below 💖\n\n"),
        _vars_src=vars_src,
        check=(meta.get("check") or "output").strip(),
        _raw={
            "learn": learn,
            "instructions": instructions,
            "hint": hint,
            "solution": solution,
            "expect": meta.get("expect", ""),
        },
    )
    level.roll()
    return level


# --------------------------------------------------------------------------- #
#  Random values and templates
# --------------------------------------------------------------------------- #

_VAR_NAMESPACE = {
    "randint": random.randint,
    "randrange": random.randrange,
    "choice": random.choice,
    "choices": random.choices,
    "uniform": random.uniform,
    "sample": random.sample,
    "shuffle": random.shuffle,
    "random": random.random,
    "round": round,
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "sorted": sorted,
    "str": str,
    "int": int,
    "float": float,
    "list": list,
    "range": range,
    "enumerate": enumerate,
    "zip": zip,
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "repr": repr,
}


def _run_vars(source: str, seed: int | None) -> dict:
    """Execute the `<vars>` block and return the names it defined.

    The block is ordinary Python: `x = randint(1, 10)` or
    `city = choice(['Oslo', 'Lima'])`. Later lines can use earlier names, so
    derived values (like a computed total) stay consistent with the inputs.
    """
    if not source.strip():
        return {}
    saved = random.getstate()
    if seed is not None:
        random.seed(seed)
    scope = dict(_VAR_NAMESPACE)
    try:
        exec(compile(source, "<vars>", "exec"), scope)
    finally:
        if seed is not None:
            random.setstate(saved)
    return {k: v for k, v in scope.items() if not k.startswith("_") and k not in _VAR_NAMESPACE}


def _fmt(value, literal: bool = False) -> str:
    """Render a value the way the lesson text wants it.

    A list becomes newline-joined lines, because in a lesson template a list
    nearly always means "print each of these". A float keeps Python's own
    repr so it matches `print()` exactly.
    """
    if isinstance(value, (list, tuple)):
        if literal:
            return repr(list(value))
        return "\n".join(str(v) for v in value)
    return str(value)


def _fill(text: str, values: dict, literal: bool = False) -> str:
    """Replace `{{expression}}` with the value of that expression.

    A template may be a plain name (`{{total}}`) or a full expression
    (`{{[f"{i}. {t}" for i, t in enumerate(items)]}}`), which is what makes
    it possible to write a list or a comprehension straight into `expect`.
    Anything that fails to evaluate is left untouched, so a stray `{{` in
    prose is not an error.
    """
    if not text:
        return text

    scope = dict(_VAR_NAMESPACE)
    scope.update(values)

    def replace(match: re.Match) -> str:
        expr = match.group(1).strip()
        try:
            return _fmt(eval(expr, {"__builtins__": {}}, scope), literal)
        except Exception:
            return match.group(0)

    return _VAR_REF.sub(replace, text)


def _is_table(lines: list[str]) -> bool:
    """A GitHub-style table: a header row, a rule, then rows."""
    if len(lines) < 3:
        return False
    if not all(l.strip().startswith("|") for l in lines[:3]):
        return False
    rule = lines[1].strip()
    return bool(re.fullmatch(r"\|[\s:|-]+\|", rule)) and "-" in rule


def _split_row(line: str) -> list[str]:
    """Cells of a `| a | b |` row, keeping escaped pipes inside the cell."""
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in body:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    cells.append("".join(current).strip())
    return cells


def _table_block(lines: list[str]) -> Block:
    """Store a table as `header | cell | cell` lines plus its alignment.

    The renderer draws the box, so the source file only has to say what the
    data is — a table written by hand in ASCII is unreadable in the `.md` and
    has to be re-aligned whenever a word changes.
    """
    header = _split_row(lines[0])
    align = []
    for cell in _split_row(lines[1]):
        left = cell.startswith(":")
        right = cell.endswith(":")
        align.append("center" if left and right else
                     "right" if right else "left")
    rows = [_split_row(l) for l in lines[2:] if l.strip().startswith("|")]
    payload = "\x1f".join([
        "|".join(header),
        ",".join(align),
        "\x1e".join("|".join(r) for r in rows),
    ])
    return Block("table", payload)


def _render_block(block: Block, values: dict) -> Block:
    # code blocks are Python source, so a list there must stay a literal
    literal = block.kind == "code"
    return Block(block.kind, _fill(block.text, values, literal), block.lang)


# --------------------------------------------------------------------------- #
#  Course
# --------------------------------------------------------------------------- #


def load_course(folder: str | Path) -> list[CourseModule]:
    """Read every `*.md` in `folder` and group the levels by module number."""
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"lesson folder not found: {folder}")

    levels: list[Level] = []
    for path in sorted(folder.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        levels.append(parse_level(path))

    by_module: dict[int, list[Level]] = {}
    for level in levels:
        by_module.setdefault(level.module, []).append(level)

    modules: list[CourseModule] = []
    for number in sorted(by_module):
        modules.append(
            CourseModule(
                number=number,
                title=MODULE_TITLES.get(number, f"Module {number}"),
                blurb=MODULE_BLURBS.get(number, ""),
                levels=sorted(by_module[number], key=lambda l: l.order),
            )
        )
    return modules


#: Module titles live here rather than in the level files: a module is a
#: grouping, not a lesson, and every level would otherwise repeat it.
MODULE_TITLES = {
    1: "Langkah Pertama",
    2: "Nilai & Matematika",
    3: "Percabangan",
    4: "Perulangan",
    5: "Koleksi Data",
    6: "Fungsi",
    7: "Objek",
    8: "Modul Bawaan",
}

MODULE_BLURBS = {
    1: "Baris pertama Python-mu: mencetak pesan dan menggambar dengan teks.",
    2: "Simpan nilai di dalam nama, lalu hitung dengan nilai itu — termasuk "
       "konversi satuan yang kamu temui sehari-hari.",
    3: "Ajari program memilih, memakai perbandingan, if / elif / else, dan "
       "operator logika.",
    4: "Buat Python mengulang pekerjaan untukmu dengan while, for, dan "
       "penghitung.",
    5: "Simpan banyak nilai dalam satu list, lalu hitung dan telusuri "
       "isinya.",
    6: "Tulis sepotong kode sekali, beri nama, dan panggil sesering yang "
       "kamu mau.",
    7: "Definisikan tipe buatanmu sendiri dengan class, supaya kodemu bisa "
       "memodelkan objek nyata.",
    8: "Manfaatkan pustaka standar Python dan pakai ulang kode yang sudah "
       "ditulis orang lain.",
}
