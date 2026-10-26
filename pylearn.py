"""
pylearn — a terminal course for learning Python, built with Textual.

    python pylearn.py

Keys:  ctrl+r / F5 = Run     ctrl+s = Submit answer     ctrl+q = Quit
Mouse: everything is clickable (works in Termux too).
"""

from __future__ import annotations

import ast
import asyncio
import json
import math
import random
import re
import sys

from pathlib import Path

from dataclasses import dataclass

from collections import defaultdict

from pygments.lexers import PythonLexer
from pygments.token import Token
from rich.segment import Segment
from rich.style import Style
from rich.text import Text

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget
from textual.widgets import Button, Input, Label, RichLog, Static, TextArea
from textual.widgets.text_area import TextAreaTheme

# --------------------------------------------------------------------------- #
#  Confetti — particle overlay, ported from canvas-confetti v1.9.3
# --------------------------------------------------------------------------- #
#
# Terminal has no pixels, so every px value is converted: one row = 16 px, one
# column = 8 px, and the burst is scaled to the screen height so it reaches the
# top on a 20-row terminal as well as a 50-row one.
#
# Physics, per 1/60 s tick:
#
#     x += cos(angle2D) * velocity + drift
#     y += sin(angle2D) * velocity + gravity
#     velocity *= decay
#     wobble += wobbleSpeed
#     tiltAngle += 0.1
#
# `gravity` is added to the POSITION, not the velocity, and velocity decays —
# that is why a mote glides up, hangs, then drifts down, instead of stopping.
#
# Textual cannot alpha-blend widgets, so before launching we "photograph" the
# screen (`capture_backdrop`) and use that photo as each row's backdrop. The
# overlay removes itself when the last particle dies.
#
# `capture_backdrop` uses one internal Textual API (`_compositor`); if that
# changes there is a plain-background fallback.

import time
from functools import lru_cache

from rich.cells import cell_len

from textual.color import Color

# --------------------------------------------------------------------------
# konstanta canvas-confetti (jangan diubah: ini angka asli library)
# --------------------------------------------------------------------------

TICK_RATE = 60
"""canvas-confetti memakai requestAnimationFrame, jadi semua angka velocity
dan decay di bawah ini dihitung per 1/60 detik."""

DEFAULT_ANGLE = 90.0
DEFAULT_SPREAD = 45.0
DEFAULT_START_VELOCITY = 45.0
DEFAULT_DECAY = 0.9
DEFAULT_GRAVITY = 1.0
DEFAULT_TICKS = 200
DEFAULT_SCALAR = 1.0

#: Konfigurasi embed.im/confetti: 4 tembakan, tiap tembakan 5 sub-burst
#: (rasio, opsi). `angle=None` berarti pakai default 90 derajat (lurus ke atas).
EMBED_SHOTS = (
    # (jeda ms, angle derajat)
    (0, None),
    (700, 120.0),
    (1400, 45.0),
    (2100, None),
)
EMBED_BURSTS = (
    (0.25, {"spread": 26.0, "startVelocity": 55.0}),
    (0.20, {"spread": 60.0}),
    (0.35, {"spread": 100.0, "decay": 0.91, "scalar": 0.8}),
    (0.10, {"spread": 120.0, "startVelocity": 25.0, "decay": 0.92, "scalar": 1.2}),
    (0.10, {"spread": 120.0, "startVelocity": 45.0}),
)

# --------------------------------------------------------------------------
# tuning terminal
# --------------------------------------------------------------------------

CONFETTI_FPS = 30
"""Frame yang digambar per detik. Fisikanya tetap dihitung 60x/detik, jadi
gerakannya sama dengan aslinya walau gambar 30 fps."""

CELL_W = 8.0
"""Lebar satu kolom dalam 'piksel' acuan canvas-confetti."""

CELL_H = 16.0
"""Tinggi satu baris dalam 'piksel' acuan canvas-confetti."""

REF_CANVAS_H = 900.0
"""Tinggi canvas acuan. Semua jarak px diskalakan ke tinggi layar nyata lewat
rasio ini, supaya ledakan selalu mencapai atas layar."""

CONFETTI_DENSITY = 0.055
"""Partikel per sel layar, untuk SATU tembakan. 100x30 = 3000 sel -> ~165."""

MAX_PARTICLES = 420
"""Batas keras partikel hidup. Di layar besar tanpa batas ini animasinya
terlalu ramai dan berat."""

FADE_TO = Color.parse("#0b0b14")
"""Warna tujuan saat partikel memudar (samakan dengan background app)."""

BAND = Color.parse("#20143a")
"""Warna pita di belakang banner, supaya teks tetap terbaca di atas UI."""

#: Palet default canvas-confetti.
CONFETTI_PALETTE = (
    Color.parse("#26ccff"),
    Color.parse("#a25afd"),
    Color.parse("#ff5e7e"),
    Color.parse("#88ff5a"),
    Color.parse("#fcff42"),
    Color.parse("#ffa62d"),
    Color.parse("#ff36ff"),
)

CONFETTI_MUTED = (
    Color.parse("#4a4a5a"),
    Color.parse("#6b6b7d"),
    Color.parse("#8a8a9a"),
)

# --------------------------------------------------------------------------
# glyph: kertas berputar = bentuk berubah dari tipis (sisi) ke penuh (muka)
# --------------------------------------------------------------------------

_RAW_FACE = {
    # |sin(tilt)| rendah -> kertas terlihat dari samping (tipis)
    "edge": ("▬", "▪", "▫", "-", "=", "~"),
    # setengah miring
    "half": ("▮", "▰", "◆", "❖", "▲", "▼"),
    # menghadap penuh -> digambar sebagai sel penuh (lihat Particle.solid)
    "full": ("█", "▓"),
}


def _single_width(glyphs: tuple[str, ...]) -> tuple[str, ...]:
    """Buang glyph yang lebarnya bukan 1 sel. Emoji 2 sel akan menggeser
    baris, jadi tidak dipakai."""
    return tuple(g for g in glyphs if cell_len(g) == 1)


FACE = {kind: _single_width(chars) for kind, chars in _RAW_FACE.items()}


# --------------------------------------------------------------------------
# partikel
# --------------------------------------------------------------------------


@dataclass
class Particle:
    """Satu keping confetti, dalam satuan sel (float).

    Nama field sengaja mengikuti canvas-confetti supaya mudah dicocokkan
    dengan sumbernya.
    """

    x: float
    y: float
    vx: float
    """cos(angle2D) * velocity, sudah dalam kolom per tick."""
    vy: float
    """sin(angle2D) * velocity, sudah dalam baris per tick."""
    color: Color
    decay: float
    gravity: float
    """Ditambahkan ke POSISI tiap tick (bukan ke velocity), seperti aslinya."""
    drift: float
    tick: int = 0
    total_ticks: int = DEFAULT_TICKS
    wobble: float = 0.0
    wobble_speed: float = 0.07
    tilt: float = 0.0
    tilt_speed: float = 0.1
    scalar: float = DEFAULT_SCALAR

    @property
    def dead(self) -> bool:
        return self.tick >= self.total_ticks

    @property
    def alpha(self) -> float:
        """canvas-confetti: alpha = 1 - tick/totalTicks."""
        return max(0.0, 1.0 - self.tick / self.total_ticks)

    @property
    def face(self) -> float:
        """Seberapa 'menghadap' kertas ke layar. 0 = dari samping (tipis),
        1 = menghadap penuh. Diambil dari |sin(tilt)|."""
        return abs(math.sin(self.tilt))

    @property
    def solid(self) -> bool:
        """Kertas yang menghadap penuh digambar sebagai sel penuh berwarna,
        bukan glyph — inilah yang bikin partikelnya terlihat tebal."""
        return self.face > 0.8

    def glyph(self) -> str:
        if self.face < 0.35:
            pool = FACE["edge"]
        else:
            pool = FACE["half"]
        return pool[int(self.wobble * 6 + self.tick) % len(pool)]


# --------------------------------------------------------------------------
# style cache
# --------------------------------------------------------------------------

_ALPHA_STEPS = (0.16, 0.30, 0.44, 0.58, 0.72, 0.86, 1.0)
"""Tabel NAIK dari pudar ke pekat, karena indeksnya dihitung dari alpha.
Membuat objek rich Style mahal (~10 us); dengan ratusan partikel per frame
itu jadi puluhan milidetik, jadi alpha dikuantisasi ke tabel ini agar style
bisa di-cache."""


@lru_cache(maxsize=8192)
def _shade(color: Color, alpha: float) -> object:
    """Warna partikel yang sudah dicampur ke warna latar (untuk fade)."""
    return color.blend(FADE_TO, 1.0 - alpha).rich_color


@lru_cache(maxsize=16384)
def _particle_style(shade: object, bg: object, bold: bool, dim: bool) -> Style:
    return Style(color=shade, bgcolor=bg, bold=bold, dim=dim)


@lru_cache(maxsize=1024)
def _bg_style(bg: object) -> Style:
    return Style(bgcolor=bg)


@lru_cache(maxsize=1024)
def _solid_style(shade: object) -> Style:
    """Kertas tebal: satu sel penuh berwarna."""
    return Style(bgcolor=shade, color=shade)


# --------------------------------------------------------------------------
# foto layar (latar overlay)
# --------------------------------------------------------------------------

Cell = tuple[str, Style | None]


def capture_backdrop(screen) -> tuple[list[list[Cell]], int, int, Style | None]:
    """Foto isi layar sekarang, per sel, plus style latar untuk sel baru.

    Mengembalikan `(rows, width, height, fill_style)`. Kalau API internal
    berubah, `rows` kosong dan pemanggil memakai `fill_style` sebagai latar.
    """
    width, height = screen.size
    background = getattr(screen.styles, "background", None)
    fill_style = Style(bgcolor=background.rich_color) if background else None

    rows: list[list[Cell]] = []
    try:
        update = screen._compositor.render_update(full=True)
        for line in update.strips:
            cells: list[Cell] = []
            for strip in line:
                for segment in strip:
                    if segment.control:
                        continue
                    for char in segment.text:
                        cells.append((char, segment.style))
                        if cell_len(char) == 2:
                            cells.append(("", segment.style))  # sel lanjutan
            rows.append(cells)
    except Exception:  # pragma: no cover - jaring pengaman
        rows = []

    if not rows:
        blank: list[Cell] = [(" ", fill_style)] * width
    else:
        blank = [(" ", None)] * width

    while len(rows) < height:
        rows.append(list(blank))
    return [row[:width] for row in rows[:height]], width, height, fill_style


def _cells_to_segments(cells: list[Cell]) -> list[Segment]:
    """Gabungkan sel dengan style sama jadi satu segmen (lebih sedikit
    escape code, lebih hemat bandwidth terminal)."""
    segments: list[Segment] = []
    buffer: list[str] = []
    style: Style | None = None
    for char, cell_style in cells:
        if char == "":
            continue  # sel lanjutan karakter lebar
        if cell_style is not style:
            if buffer:
                segments.append(Segment("".join(buffer), style))
            buffer = []
            style = cell_style
        buffer.append(char)
    if buffer:
        segments.append(Segment("".join(buffer), style))
    return segments


def _row_backgrounds(rows: list[list[Cell]], fill: Style | None) -> list[list[object]]:
    """Ambil warna latar tiap sel dari foto layar.

    Partikel menimpa karakter tapi harus tetap duduk di atas latar yang sama
    (mis. tombol hijau). Tanpa ini, sel partikel jadi "lubang" gelap karena
    tidak punya bgcolor sama sekali.
    """
    fallback = None if fill is None else fill.bgcolor
    out: list[list[object]] = []
    for row in rows:
        backgrounds: list[object] = []
        for _char, style in row:
            bg = None
            if style is not None:
                if style.reverse:
                    # sel terbalik: warna latarnya adalah warna teks aslinya
                    bg = style.color or fallback
                else:
                    bg = style.bgcolor
            backgrounds.append(bg if bg is not None else fallback)
        out.append(backgrounds)
    return out


# --------------------------------------------------------------------------
# overlay
# --------------------------------------------------------------------------


class Confetti(Widget):
    """Overlay partikel sekali pakai: setelah semua partikel mati, dia
    menghapus dirinya sendiri dari layar."""

    DEFAULT_CSS = """
    Confetti {
        layer: confetti;
        position: absolute;
        offset: 0 0;
        width: 100%;
        height: 100%;
        background: transparent;
    }
    """

    def __init__(
        self,
        rows: list[list[Cell]],
        width: int,
        height: int,
        *,
        fill_style: Style | None = None,
        banner: str | None = None,
        seed: int | None = None,
        density: float = CONFETTI_DENSITY,
        autolaunch: bool = True,
        shots: int | None = None,
    ) -> None:
        super().__init__()
        self._rows = rows
        self._width = width
        self._height = height
        self._fill_style = fill_style
        self._banner = banner
        self._density = density
        self._autolaunch = autolaunch
        self._shots = len(EMBED_SHOTS) if shots is None else max(0, shots)
        self._rand = random.Random(seed)
        self._particles: list[Particle] = []
        self._frame: dict[int, dict[int, tuple[str, Style]]] = {}
        self._rows_strip = [Strip(_cells_to_segments(row), width) for row in rows]
        self._row_bg = _row_backgrounds(rows, fill_style)

        # skala: px acuan -> sel terminal
        self._scale = (height * CELL_H) / REF_CANVAS_H
        self._pending: list[tuple[float, float | None, int]] = []
        """Tembakan yang belum keluar: (waktu_ms, angle, jumlah partikel)."""
        self._clock = 0.0
        self._banner_age = 0.0
        self._banner_life = 2.0
        self._last = time.monotonic()
        self._timer = None
        self._finished = False

    # -- lifecycle ---------------------------------------------------------

    def on_mount(self) -> None:
        self._last = time.monotonic()
        self._timer = self.set_interval(1 / CONFETTI_FPS, self._tick)
        if self._autolaunch:
            self._launch()

    def on_resize(self) -> None:
        """Terminal di-resize saat animasi jalan: sesuaikan kanvas."""
        width, height = self.size
        if not width or not height:
            return
        if width == self._width and height == self._height:
            return
        blank: Cell = (" ", self._fill_style)
        rows: list[list[Cell]] = []
        for y in range(height):
            if y < len(self._rows):
                row = self._rows[y][:width]
                row = row + [blank] * (width - len(row))
            else:
                row = [blank] * width
            rows.append(row)
        self._rows = rows
        self._width = width
        self._height = height
        self._rows_strip = [Strip(_cells_to_segments(row), width) for row in rows]
        self._row_bg = _row_backgrounds(rows, self._fill_style)
        self._scale = (height * CELL_H) / REF_CANVAS_H

    def stop(self) -> None:
        """Hentikan animasi (dipakai sebelum overlay diganti)."""
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

    # -- peluncuran --------------------------------------------------------

    def _launch(self) -> None:
        """Jadwalkan tembakan ala embed.im/confetti.

        `shots` memotong jadwal itu: `shots=1` menembak sekali saja, bukan
        empat kali dengan jeda 700 ms.
        """
        if not self._shots:
            return
        per_shot = max(30, int(self._width * self._height * self._density))
        per_shot = min(per_shot, MAX_PARTICLES // self._shots)
        self._pending = [
            (float(delay), angle, per_shot) for delay, angle in EMBED_SHOTS[: self._shots]
        ]

    def fire(self, angle: float | None = None, count: int | None = None) -> None:
        """Satu tembakan = 5 sub-burst dengan rasio dan opsi dari embed.im."""
        total = count if count is not None else max(
            30, int(self._width * self._height * self._density)
        )
        for ratio, opts in EMBED_BURSTS:
            self.burst(
                count=int(total * ratio),
                angle=angle,
                spread=opts.get("spread", DEFAULT_SPREAD),
                start_velocity=opts.get("startVelocity", DEFAULT_START_VELOCITY),
                decay=opts.get("decay", 0.93),
                scalar=opts.get("scalar", DEFAULT_SCALAR),
                colors=CONFETTI_PALETTE,
            )

    def burst(
        self,
        *,
        count: int,
        angle: float | None = None,
        spread: float = DEFAULT_SPREAD,
        start_velocity: float = DEFAULT_START_VELOCITY,
        decay: float = 0.93,
        scalar: float = DEFAULT_SCALAR,
        gravity: float = DEFAULT_GRAVITY,
        drift: float = 0.0,
        ticks: int = DEFAULT_TICKS,
        colors: tuple[Color, ...] = CONFETTI_PALETTE,
    ) -> None:
        """Semburkan partikel dari titik asal, persis `randomPhysics` +
        `updateFetti` di canvas-confetti."""
        if count <= 0:
            return
        rand = self._rand
        origin_x = self._width / 2.0
        origin_y = float(self._height - 1)  # origin {y: 1} = dasar layar

        angle = DEFAULT_ANGLE if angle is None else angle
        rad_angle = math.radians(angle)
        rad_spread = math.radians(spread)
        scale = self._scale

        for i in range(count):
            # velocity: setengah startVelocity + acak sampai startVelocity penuh
            velocity = (start_velocity * 0.5) + rand.random() * start_velocity
            angle2d = -rad_angle + (0.5 * rad_spread - rand.random() * rad_spread)

            # px/tick -> sel/tick, lalu diskalakan ke tinggi layar
            vx = math.cos(angle2d) * velocity * scale / CELL_W
            vy = math.sin(angle2d) * velocity * scale / CELL_H

            self._particles.append(
                Particle(
                    x=origin_x,
                    y=origin_y,
                    vx=vx,
                    vy=vy,
                    color=colors[i % len(colors)],
                    decay=decay,
                    gravity=gravity * scale / CELL_H,
                    drift=drift * scale / CELL_W,
                    total_ticks=ticks,
                    wobble=rand.random() * 10.0,
                    wobble_speed=min(0.11, rand.random() * 0.1 + 0.05),
                    tilt=(rand.random() * (0.75 - 0.25) + 0.25) * math.pi,
                    scalar=scalar,
                )
            )

    def puff(self) -> None:
        """Versi kecil & kelabu — untuk jawaban salah.

        Reads as a gust of wind, not an explosion: motes start scattered over
        the whole frame instead of erupting from one point, drift slowly
        sideways, and fade out where they are. A bottom-anchored burst with
        fast decay reads as "pop", which is the wrong signal here.
        """
        self._particles.clear()
        self._pending.clear()
        self._banner = None
        if self._timer is None:
            self._timer = self.set_interval(1 / CONFETTI_FPS, self._tick)

        rand = self._rand
        for index in range(55):
            # anywhere in the frame, biased towards the middle band
            x = rand.uniform(0, max(1, self._width - 1))
            y = rand.uniform(0, max(1, self._height - 1))
            # a slow sideways push, alternating direction
            direction = -1 if rand.random() < 0.5 else 1
            speed = rand.uniform(0.03, 0.10) * direction
            self._particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=speed,
                    vy=rand.uniform(0.005, 0.03),
                    color=CONFETTI_MUTED[index % len(CONFETTI_MUTED)],
                    decay=0.999,               # almost no drag: keeps drifting
                    gravity=rand.uniform(0.006, 0.018),
                    drift=rand.uniform(-0.05, 0.05),
                    total_ticks=rand.randint(900, 1500),
                    wobble=rand.random() * 10.0,
                    wobble_speed=min(0.11, rand.random() * 0.06 + 0.03),
                    tilt=rand.random() * math.pi,
                )
            )
        if self._timer is None:
            self._timer = self.set_interval(1 / CONFETTI_FPS, self._tick)

    # -- animasi -----------------------------------------------------------

    def _tick(self) -> None:
        now = time.monotonic()
        dt = min(now - self._last, 0.08)  # clamp: jangan lompat kalau lag
        self._last = now

        self._banner_age += dt
        self._clock += dt * 1000.0

        # jadwal tembakan (ms), sama seperti setTimeout di embed.im
        while self._pending and self._pending[0][0] <= self._clock:
            _delay, angle, count = self._pending.pop(0)
            self.fire(angle, count)

        self._step(dt)
        self._build_frame()
        self.refresh()

        if not self._particles and not self._pending:
            self._finish()

    def _step(self, dt: float) -> None:
        """Jalankan fisika dalam tick 1/60 s, berapa pun fps gambarnya."""
        ticks = dt * TICK_RATE
        whole = int(ticks)
        frac = ticks - whole
        alive: list[Particle] = []

        for p in self._particles:
            # tick bulat: pakai rumus asli persis
            for _ in range(whole):
                p.x += p.vx + p.drift
                p.y += p.vy + p.gravity
                p.vx *= p.decay
                p.vy *= p.decay
                p.wobble += p.wobble_speed
                p.tilt += p.tilt_speed
                p.tick += 1
            if frac > 0:
                p.x += (p.vx + p.drift) * frac
                p.y += (p.vy + p.gravity) * frac
                p.vx *= p.decay**frac
                p.vy *= p.decay**frac
                p.wobble += p.wobble_speed * frac
                p.tilt += p.tilt_speed * frac

            if p.dead or p.y > self._height + 2:
                continue
            if p.x < -4 or p.x > self._width + 4:
                continue
            alive.append(p)
        self._particles = alive

    def _build_frame(self) -> None:
        frame: dict[int, dict[int, tuple[str, Style]]] = {}
        width, height = self._width, self._height
        row_bg = self._row_bg
        steps = _ALPHA_STEPS
        last = len(steps) - 1

        def put(ix: int, iy: int, glyph: str, style: Style) -> None:
            if 0 <= ix < width and 0 <= iy < height:
                frame.setdefault(iy, {})[ix] = (glyph, style)

        for p in self._particles:
            alpha = p.alpha
            if alpha <= 0.06:
                continue
            level = steps[int(alpha * last + 0.5)]
            shade = _shade(p.color, level)
            ix, iy = int(p.x), int(p.y)

            if p.solid:
                put(ix, iy, " ", _solid_style(shade))
            else:
                # partikel menimpa karakter, bukan latarnya: warisi bgcolor
                # sel asal supaya tombol/panel di bawah tetap terlihat
                bg = None
                if 0 <= iy < height and 0 <= ix < width:
                    bg = row_bg[iy][ix]
                put(ix, iy, p.glyph(),
                    _particle_style(shade, bg, level > 0.5, level < 0.35))

        self._banner_cells(put)
        self._frame = frame

    def _banner_cells(self, put) -> None:
        if not self._banner or self._banner_age > self._banner_life:
            return
        t = self._banner_age / self._banner_life
        alpha = 1.0 if t < 0.65 else max(0.0, (1.0 - t) / 0.35)
        level = _ALPHA_STEPS[int(alpha * (len(_ALPHA_STEPS) - 1) + 0.5)]

        text = f"  {self._banner}  "
        x0 = max(0, (self._width - len(text)) // 2)
        y0 = max(1, self._height // 3)
        shift = int(self._banner_age * 14)

        band = _bg_style(_shade(BAND, level))
        for x in range(x0, min(x0 + len(text), self._width)):
            put(x, y0, " ", band)
        for i, char in enumerate(text):
            color = _shade(CONFETTI_PALETTE[(i + shift) % len(CONFETTI_PALETTE)], level)
            put(x0 + i, y0, char, _particle_style(color, band.bgcolor, True, False))

    def _finish(self) -> None:
        if self._finished:
            return
        self._finished = True
        self.stop()
        self.remove()

    # -- render ------------------------------------------------------------

    def render_line(self, y: int) -> Strip:
        if not (0 <= y < len(self._rows_strip)):
            return Strip.blank(self._width)
        cells = self._frame.get(y)
        if not cells:
            return self._rows_strip[y]

        base = self._rows[y]
        width = self._width
        out: list[Cell] = []
        x = 0
        while x < width:
            hit = cells.get(x)
            if hit is not None:
                out.append(hit)
                x += 1
                continue

            char, style = base[x]
            if char == "":  # sel lanjutan tanpa karakter utama
                out.append((" ", None))
                x += 1
                continue
            if cell_len(char) == 2:
                # karakter lebar: jangan pecah kalau sel keduanya ketutup
                if x + 1 < width and cells.get(x + 1) is not None:
                    out.append((" ", None))
                    out.append((" ", None))
                else:
                    out.append((char, style))
                    out.append(("", style))
                x += 2
                continue
            out.append((char, style))
            x += 1

        return Strip(_cells_to_segments(out), width)

    def render_lines(self, crop) -> list[Strip]:
        return [self.render_line(y) for y in range(crop.height)]


# --------------------------------------------------------------------------
# API satu baris
# --------------------------------------------------------------------------


def _spawn(
    screen, banner: str | None, density: float, puff: bool = False,
    shots: int | None = None,
) -> Confetti:
    """Pasang overlay baru; `puff=True` memakai efek kelabu (jawaban salah)."""
    rows, width, height, fill = capture_backdrop(screen)
    widget = Confetti(
        rows, width, height,
        fill_style=fill, banner=banner, density=density, autolaunch=not puff,
        shots=shots,
    )
    screen.mount(widget)
    if puff:
        widget.puff()
    return widget


def celebrate(
    screen, banner: str | None = "CORRECT!", *, density: float = CONFETTI_DENSITY,
    shots: int | None = None,
) -> None:
    """Nyalakan confetti di layar ini. Aman dipanggil berkali-kali.

    Overlay lama dibuang dulu dan yang baru dipasang setelah layar selesai
    repaint, supaya foto latarnya bersih (tidak memotret sisa confetti).
    """
    existing = list(screen.query(Confetti))
    for widget in existing:
        widget.stop()
        widget.remove()
    if existing:
        screen.call_after_refresh(lambda: _spawn(screen, banner, density, shots=shots))
    else:
        _spawn(screen, banner, density, shots=shots)


def puff(screen) -> None:
    """Efek kecil kelabu untuk jawaban salah."""
    existing = list(screen.query(Confetti))
    for widget in existing:
        widget.stop()
        widget.remove()
    if existing:
        screen.call_after_refresh(lambda: _spawn(screen, None, CONFETTI_DENSITY, puff=True))
    else:
        _spawn(screen, None, CONFETTI_DENSITY, puff=True)

# --------------------------------------------------------------------------- #
#  Palette
# --------------------------------------------------------------------------- #
# "Midnight" — cool navy, one blue accent, syntax colours that stay legible
# on the editor. Every text/background pair here clears WCAG AA (4.5:1);
# the old white-on-blue button label sat at 2.88:1 and failed.
BG = "#0a0f1e"          # page / lesson background
PANEL = "#161d30"       # section headers, terminal header, tab strip
CODEBG = "#111827"      # code blocks inside the lesson
HELPBG = "#0f1626"      # Hint / Solution rows
EDITOR = "#101b33"      # deep navy editor
LINE = "#243049"        # divider lines
TEXT = "#e9eef8"
MUTED = "#94a3bd"
LINK = "#7cb0ff"
ORANGE = "#ffa657"
STRING = "#a5d6ff"
GREEN = "#7ee787"

HEADTEXT = "#cdd7ea"    # labels sitting on PANEL
GUTTER = "#7d90b8"      # editor line numbers
COMMENT = "#8b9dc0"     # editor comments
KEYWORD = "#ff7b72"     # editor keywords
NUMBER = "#79c0ff"      # editor numbers
ERROR = "#ff7b72"       # terminal stderr
BTN = "#1c64d9"         # primary button fill (white label: 5.42:1)
BTN_HOVER = "#1a5fd0"
BTN_DOWN = "#1857c2"
BTN_EDGE = "#5b9bf5"
BTN_SHADOW = "#123a7a"
BTN_DARK = "#111a2e"    # secondary button fill
BTN_DARK_EDGE = "#c3cfe2"
BTN_DARK_SHADOW = "#28324a"
BTN_DARK_HOVER = "#1a2438"

# ── main-menu scene ────────────────────────────────────────────────────────
SKY_TOP = "#0b1226"      # sky at the top of the frame
SKY_LOW = "#22304f"      # sky just above the skyline
STAR = "#9fb0d0"
BUILDING = "#070c18"     # silhouettes, darker than any sky tone
BUILDING_EDGE = "#2b3a5c"
WINDOW_WARM = "#ffd166"
WINDOW_COOL = "#6ea8fe"
RAIN_NEAR = "#9db4d8"
RAIN_FAR = "#44506e"
TITLE_TOP = "#6ea8fe"    # block title gradient: blue …
TITLE_BOTTOM = "#ffd166" # … to yellow, Python's two colours
TITLE_SHADOW = "#070c1a"
YELLOW = "#ffe14d"       # Start button frame and label (bright)
SEA = "#2f93cf"          # open water: what the Start button sits on
YELLOW_INK = "#23180a"   # label on a solid yellow fill
SAND = "#f6e6bd"         # beach sand: what the Start button sits on

STARTER_CODE = "# Write code below 💖\n\n"

# --------------------------------------------------------------------------- #
#  Tiny pixel-art sprites (rendered with half blocks, 2 pixels per text row)
# --------------------------------------------------------------------------- #
PALETTE = {
    "g": "#2f9e44", "G": "#74d680", "w": "#f4f4f4", "k": "#1a1a2e",
    "r": "#e03131", "R": "#ff6b6b", "s": "#f1c27d", "b": "#3b5bdb",
    "h": "#7a4a21", "y": "#f5c542", "p": "#6c757d", "W": "#cfd8e3",
}

SNAKE = [
    "....ggg..",
    "...gGGGg.",
    "...gGwkg.",
    "...gGGGgr",
    "....gGgg.",
    "...ggg...",
    "..gGGg...",
    "..gGgggg.",
    "...gGGGGg",
    "....gggg.",
]
HERO = [
    "...rrr...",
    "..rRRRr..",
    "...sss...",
    "..sksks..",
    "...sss...",
    "..bbbbb..",
    ".sbbbbbs.",
    "..bbbbb..",
    "..b...b..",
    "..k...k..",
]
KID = [
    "..hhh..",
    ".hhhhh.",
    ".sksks.",
    "..sss..",
    ".rrrrr.",
    "rrrrrrr",
    ".r...r.",
    ".k...k.",
]
SKULL = [
    "..WWW..",
    ".WkWkW.",
    ".WWWWW.",
    "..WpW..",
    ".ppppp.",
    "p.ppp.p",
    "..p.p..",
    "..k.k..",
]


SPRITES = {
    "snake": SNAKE,
    "hero": HERO,
    "skull": SKULL,
}


def sprite_row(sprites: list[list[str]], height: int = 10, gap: int = 1) -> Text:
    """Place sprites side by side (bottom aligned) and render with ▀ ▄ half blocks."""
    padded: list[list[str]] = []
    for sp in sprites:
        w = max(len(r) for r in sp)
        rows = [r.ljust(w, ".") for r in sp]
        rows = ["." * w] * (height - len(rows)) + rows
        padded.append(rows)
    grid = []
    for y in range(height):
        grid.append(("." * gap).join(sp[y] for sp in padded))
    out = Text()
    for y in range(0, height, 2):
        top, bot = grid[y], grid[y + 1]
        for t, b in zip(top, bot):
            tc, bc = PALETTE.get(t), PALETTE.get(b)
            if tc and bc:
                out.append("▀", Style(color=tc, bgcolor=bc))
            elif tc:
                out.append("▀", Style(color=tc))
            elif bc:
                out.append("▄", Style(color=bc))
            else:
                out.append(" ")
        out.append("\n")
    out.rstrip()
    return out


# --------------------------------------------------------------------------- #
#  Widgets
# --------------------------------------------------------------------------- #
class ProgressBar(Static):
    """Whole-course progress pill in the top bar.

    It tracks the finished levels, not the current exercise, so the number
    means the same thing on the level picker and inside a lesson.
    """

    pct = 0
    accent = GREEN

    def render(self) -> Text:
        w = max(self.size.width, 6)
        inner = w - 2
        # a partly filled pill at 0% would read as progress that is not there
        fill = round(inner * self.pct / 100)
        if self.pct and not fill:
            fill = 1
        t = Text(no_wrap=True)
        t.append("▐", Style(color="#26314a"))
        t.append(" " * fill, Style(bgcolor=self.accent))
        t.append(" " * (inner - fill), Style(bgcolor="#1e2740"))
        t.append("▌", Style(color="#26314a"))
        return t

    def set_pct(self, pct: int) -> None:
        self.pct = max(0, min(100, pct))
        self.refresh()


class CodeBlock(Horizontal):
    """Grey code box with the 'copy' icon on the right."""

    def __init__(self, markup: str, raw: str) -> None:
        super().__init__(classes="code-block")
        self.markup, self.raw = markup, raw

    def compose(self) -> ComposeResult:
        yield Static(self.markup, classes="cb-text")
        yield Static("⧉", classes="cb-copy")

    def on_click(self, event) -> None:
        if getattr(event.widget, "has_class", None) and event.widget.has_class("cb-copy"):
            self.app.copy_to_clipboard(self.raw)
            self.app.notify(f"Copied  {self.raw}", timeout=2)


class HelpItem(Vertical):
    """Hint / Walkthrough / Solution / AI row with a chevron."""

    def __init__(self, icon: str, title: str, body: str,
                 locked: bool = False, unlock_at: int = 0, failures: int = 0) -> None:
        super().__init__(classes="help-item")
        self.icon, self.title_text, self.body_text = icon, title, body
        self.locked = locked
        self.unlock_at = unlock_at
        self.failures = failures

    def compose(self) -> ComposeResult:
        with Horizontal(classes="hi-head"):
            yield Label(self.icon, classes="hi-icon")
            yield Label(self._title(), classes="hi-title")
            yield Label("⌄" if not self.locked else "·", classes="hi-chev")
        yield Static(self.body_text, classes="hi-body")

    def _title(self) -> str:
        if not self.locked:
            return self.title_text
        left = max(0, self.unlock_at - self.failures)
        return f"{self.title_text}  ·  {left} more to unlock"

    def unlock(self, failures: int) -> None:
        """Called after a failed submit: opens the body once the count is met."""
        self.failures = failures
        if self.locked and failures >= self.unlock_at:
            self.locked = False
            self.add_class("-open")
            self.query_one(".hi-chev", Label).update("⌃")
        self.query_one(".hi-title", Label).update(self._title())

    def on_click(self, event) -> None:
        if self.locked:
            left = max(0, self.unlock_at - self.failures)
            self.app.notify(
                f"Get it wrong {left} more time{'s' if left != 1 else ''} to unlock.",
                timeout=2,
            )
            return
        w = event.widget
        # only the header toggles
        if w is not None and (w.has_class("hi-head") or w.parent is not None and w.parent.has_class("hi-head")):
            self.toggle_class("-open")
            self.query_one(".hi-chev", Label).update("⌃" if self.has_class("-open") else "⌄")


# --------------------------------------------------------------------------- #
#  IntelliSense — completions drawn from the code you are writing
# --------------------------------------------------------------------------- #
#
# No language server, no tree-sitter: the editor is a single script, so the
# symbols that matter are the names this file defines — variables, functions,
# classes, parameters — plus what Python itself provides. The source is parsed
# with `ast` (exact, no regex guessing) and the member list for a name is read
# off the object it refers to, falling back to a static table for the types
# that cannot be resolved without running the code.

INTEL_KINDS = {
    "variable": "var",
    "function": "def",
    "class": "cls",
    "module": "mod",
    "keyword": "kw",
    "builtin": "fn",
    "method": "mth",
    "attribute": "attr",
    "snippet": "snip",
}

#: Members offered for a name whose type cannot be inferred statically.
_MEMBER_TABLE: dict[str, tuple[str, ...]] = {
    "str": ("capitalize", "casefold", "center", "count", "encode", "endswith",
            "find", "format", "index", "isalnum", "isalpha", "isdigit",
            "islower", "isupper", "join", "lower", "lstrip", "partition",
            "removeprefix", "removesuffix", "replace", "rfind", "rindex",
            "rpartition", "rsplit", "rstrip", "split", "splitlines",
            "startswith", "strip", "swapcase", "title", "upper", "zfill"),
    "list": ("append", "clear", "copy", "count", "extend", "index", "insert",
             "pop", "remove", "reverse", "sort"),
    "dict": ("clear", "copy", "fromkeys", "get", "items", "keys", "pop",
             "popitem", "setdefault", "update", "values"),
    "set": ("add", "clear", "copy", "difference", "discard", "intersection",
            "issubset", "issuperset", "pop", "remove", "union", "update"),
    "tuple": ("count", "index"),
}

#: Builtin callables and their parameters, in the order Python documents them.
_BUILTIN_SIGNATURES: dict[str, tuple[str, ...]] = {
    "abs": ("x",), "all": ("iterable",), "any": ("iterable",),
    "bool": ("x",), "callable": ("object",), "chr": ("i",), "ord": ("c",),
    "dict": ("**kwargs",), "divmod": ("a", "b"), "enumerate": ("iterable", "start"),
    "filter": ("function", "iterable"), "float": ("x",), "format": ("value", "format_spec"),
    "frozenset": ("iterable",), "getattr": ("object", "name", "default"),
    "hasattr": ("object", "name"), "hash": ("object",), "id": ("object",),
    "input": ("prompt",), "int": ("x", "base"), "isinstance": ("object", "classinfo"),
    "issubclass": ("cls", "classinfo"), "iter": ("iterable",), "len": ("s",),
    "list": ("iterable",), "map": ("function", "iterable"),
    "max": ("iterable", "key"), "min": ("iterable", "key"), "next": ("iterator", "default"),
    "open": ("file", "mode"), "pow": ("base", "exp"), "print": ("*values", "sep", "end"),
    "range": ("start", "stop", "step"), "repr": ("object",), "reversed": ("seq",),
    "round": ("number", "ndigits"), "set": ("iterable",), "setattr": ("object", "name", "value"),
    "sorted": ("iterable", "key", "reverse"), "str": ("object",), "sum": ("iterable", "start"),
    "tuple": ("iterable",), "type": ("object",), "zip": ("*iterables",),
}

#: Names typed in a lesson constantly; offered before user symbols.
_BUILTINS: tuple[str, ...] = tuple(_BUILTIN_SIGNATURES)

#: The order a beginner meets these in. Used only to break ties, so that the
#: first suggestion for `p` is `print` and for `r` is `range`.
_COMMON_ORDER: dict[str, int] = {
    name: index for index, name in enumerate((
        "print", "input", "range", "len", "int", "str", "float", "list",
        "dict", "sum", "min", "max", "abs", "round", "sorted", "enumerate",
        "zip", "open", "type", "isinstance", "map", "filter", "reversed",
        "bool", "set", "tuple", "pow", "pass", "object",
    ))
}

_KEYWORDS: tuple[str, ...] = (
    "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "False", "finally", "for", "from",
    "global", "if", "import", "in", "is", "lambda", "None", "nonlocal", "not",
    "or", "pass", "raise", "return", "True", "try", "while", "with", "yield",
)


@dataclass(frozen=True)
class Completion:
    """One row in the popup."""

    label: str
    kind: str
    detail: str = ""
    params: tuple[str, ...] = ()

    @property
    def callable(self) -> bool:
        """Whether accepting this should write `name()` rather than `name`.

        Mirrors `python.analysis.completeFunctionParens` in Pylance: functions
        and methods get their parentheses, variables and classes do not.
        """
        return self.kind in ("def", "fn", "mth", "builtin")

    @property
    def icon(self) -> str:
        return {"var": "𝑣", "def": "ƒ", "cls": "◆", "mod": "◫", "kw": "λ",
                "fn": "ƒ", "mth": "≡", "attr": "·"}.get(self.kind, "·")


class SymbolIndex:
    """Everything the file defines, collected from its syntax tree."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.names: dict[str, Completion] = {}
        self.members: dict[str, list[Completion]] = {}
        self.signatures: dict[str, tuple[str, ...]] = {}
        self._tree: ast.AST | None = None
        self._reindex()

    def _reindex(self) -> None:
        self.names.clear()
        self.members.clear()
        self.signatures.clear()
        self._tree = self._parse(self.source)
        if self._tree is None:
            return
        self._collect(self._tree)

    @staticmethod
    def _parse(source: str) -> ast.AST | None:
        """Parse code that is usually half-written.

        `names.` and an unclosed bracket are syntax errors, and that is the
        normal state of an editor mid-keystroke. Rather than give up, the
        offending lines are dropped and the rest of the file still yields its
        symbols — a completion list that is 95% right beats an empty one.
        """
        try:
            return ast.parse(source)
        except SyntaxError:
            pass
        lines = source.split("\n")
        for attempt in range(len(lines)):
            keep = lines[: len(lines) - attempt - 1]
            if not keep:
                break
            try:
                return ast.parse("\n".join(keep))
            except SyntaxError:
                continue
        return None

    def _add(self, name: str, kind: str, detail: str = "") -> None:
        if not name or name.startswith("_"):
            return
        self.names.setdefault(name, Completion(name, kind, detail))

    def _collect(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    for leaf in ast.walk(target):
                        if isinstance(leaf, ast.Name):
                            detail = _describe_value(node.value)
                            self._add(leaf.id, "variable", detail)
                            self._members_for(leaf.id, node.value)
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
                target = node.target
                if isinstance(target, ast.Name):
                    self._add(target.id, "variable",
                              _describe_annotation(getattr(node, "annotation", None)))
                    self._members_for(target.id, getattr(node, "value", None))
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                for leaf in ast.walk(node.target):
                    if isinstance(leaf, ast.Name):
                        self._add(leaf.id, "variable", "loop")
            elif isinstance(node, (ast.comprehension,)):
                for leaf in ast.walk(node.target):
                    if isinstance(leaf, ast.Name):
                        self._add(leaf.id, "variable", "comprehension")
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars is not None:
                        for leaf in ast.walk(item.optional_vars):
                            if isinstance(leaf, ast.Name):
                                self._add(leaf.id, "variable", "context")
                                self._members_for(leaf.id, item.context_expr)
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                self._add(node.name, "def", _signature(node))
                self.signatures[node.name] = tuple(_param_names(node))
                for arg in _all_args(node.args):
                    self._add(arg.arg, "variable", "parameter")
            elif isinstance(node, ast.ClassDef):
                self._add(node.name, "cls", "class")
                for child in node.body:
                    if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                        if not child.name.startswith("_"):
                            self.members.setdefault(node.name, []).append(
                                Completion(child.name, "mth", _signature(child),
                                           tuple(_param_names(child)))
                            )
                            self.signatures[f"{node.name}.{child.name}"] = tuple(
                                _param_names(child)
                            )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    label = alias.asname or alias.name.split(".")[0]
                    self._add(label, "mod", alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name != "*":
                        self._add(alias.asname or alias.name, "mod",
                                  f"from {node.module or ''}")
            elif isinstance(node, ast.Global | ast.Nonlocal):
                for name in node.names:
                    self._add(name, "variable", "global")

    def _members_for(self, name: str, value: ast.AST | None) -> None:
        """Remember the members of `name` when its type is obvious."""
        if value is None:
            return
        if isinstance(value, ast.Constant):
            members = _MEMBER_TABLE.get(type(value.value).__name__)
        elif isinstance(value, ast.JoinedStr):
            members = _MEMBER_TABLE["str"]
        elif isinstance(value, ast.List | ast.ListComp):
            members = _MEMBER_TABLE["list"]
        elif isinstance(value, ast.Dict | ast.DictComp):
            members = _MEMBER_TABLE["dict"]
        elif isinstance(value, ast.Set | ast.SetComp):
            members = _MEMBER_TABLE["set"]
        elif isinstance(value, ast.Tuple):
            members = _MEMBER_TABLE["tuple"]
        elif isinstance(value, ast.Call):
            func = value.func
            kind = None
            if isinstance(func, ast.Name):
                kind = {"str": "str", "list": "list", "dict": "dict",
                        "set": "set", "tuple": "tuple"}.get(func.id)
            members = _MEMBER_TABLE.get(kind) if kind else None
        else:
            members = None
        if members:
            self.members[name] = [Completion(m, "mth") for m in members]

    # -- queries --------------------------------------------------------
    def suggest(self, prefix: str, *, limit: int = 60) -> list[Completion]:
        """Names in the file that start with `prefix`, user symbols first."""
        prefix = prefix.lower()
        # Rank the way an editor does. `p` must offer `print` before `pow`:
        # in a beginner course that is what the prefix almost always means.
        # Frequency decides, then shortness, then the alphabet.
        def rank(completion: Completion) -> tuple:
            label = completion.label.lower()
            priority = _COMMON_ORDER.get(label, len(_COMMON_ORDER))
            return (label != prefix, priority, len(label), label)

        found = [c for name, c in self.names.items()
                 if name.lower().startswith(prefix)]
        found.sort(key=rank)
        found += [
            Completion(b, "builtin", _builtin_detail(b), _BUILTIN_SIGNATURES[b])
            for b in _BUILTINS if b.startswith(prefix)
        ]
        found += [Completion(k, "keyword") for k in _KEYWORDS
                  if k.startswith(prefix)]
        # builtins and keywords join the same ranking; a stable sort keeps the
        # file's own names ahead of identical-length builtins
        found.sort(key=rank)
        return found[:limit]

    def members_of(self, expr: str) -> list[Completion]:
        """Members of `expr`, resolved from the file or the static table."""
        expr = expr.strip()
        if not expr:
            return []
        # a class defined in this file
        if expr in self.members:
            return self.members[expr]
        # dotted chains: resolve the head, then the rest is a guess
        head = expr.split(".")[0]
        if head in self.members and expr == head:
            return self.members[head]
        # `"text".upper()`, `[].append`, ...
        if expr.startswith(("'", '"')):
            return [Completion(m, "mth") for m in _MEMBER_TABLE["str"]]
        if expr.startswith("["):
            return [Completion(m, "mth") for m in _MEMBER_TABLE["list"]]
        if expr.startswith("{"):
            return [Completion(m, "mth") for m in _MEMBER_TABLE["dict"]]
        # builtin constructors
        base = {"len": "int", "range": "range", "input": "str", "str": "str",
                "int": "int", "float": "float", "list": "list", "dict": "dict"}
        if expr in base and base[expr] in _MEMBER_TABLE:
            return [Completion(m, "mth") for m in _MEMBER_TABLE[base[expr]]]
        return []


def describe_mismatch(expected: str, actual: str) -> str:
    """Explain where the answer differs, in a way that can be acted on.

    `Expected '1\n     2 3', got '1\n2 3'` is technically true and useless:
    the difference is invisible whitespace. This lines the two up and marks the
    exact column, so "my spaces are wrong" becomes obvious at a glance.
    """
    want = expected.splitlines()
    got = actual.splitlines()
    if not actual:
        return "Nothing was printed."
    if want == got:
        return "The output matches, but something else failed."

    lines: list[str] = []
    if len(want) != len(got):
        lines.append(f"Expected {len(want)} line(s), got {len(got)}.")

    for index in range(max(len(want), len(got))):
        left = want[index] if index < len(want) else None
        right = got[index] if index < len(got) else None
        if left == right:
            continue
        number = index + 1
        if left is None:
            lines.append(f"  line {number}: extra line {right!r}")
            continue
        if right is None:
            lines.append(f"  line {number}: missing line {left!r}")
            continue
        # how far in the two agree, then quote the first column that differs
        column = 0
        while column < min(len(left), len(right)) and left[column] == right[column]:
            column += 1
        lines.append(f"  line {number}: expected {left!r}")
        lines.append(f"  {' ' * len(str(number))}  got      {right!r}")
        if column < len(left) and left[column] == " ":
            lines.append(f"  column {column + 1}: a space is missing here")
        elif column < len(right) and right[column] == " ":
            lines.append(f"  column {column + 1}: this space should not be here")
        else:
            lines.append(f"  they first differ at column {column + 1}")
        break

    return "\n".join(lines[:6])


def _builtin_detail(name: str) -> str:
    params = _BUILTIN_SIGNATURES.get(name, ())
    return f"({', '.join(params)})" if params else ""


def _all_args(args: ast.arguments) -> list[ast.arg]:
    out = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
    if args.vararg:
        out.append(args.vararg)
    if args.kwarg:
        out.append(args.kwarg)
    return out


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """`name(a, b=1)` — enough to recognise the call without reading the body."""
    return f"({', '.join(_param_names(node))})"


def _param_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Parameter names with their defaults folded in, for signature help."""
    parts: list[str] = []
    args = node.args
    positional = list(args.posonlyargs) + list(args.args)
    defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
    for arg, default in zip(positional, defaults):
        parts.append(arg.arg if default is None else f"{arg.arg}=…")
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        parts.append(arg.arg if default is None else f"{arg.arg}=…")
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    return parts


def _describe_value(value: ast.AST) -> str:
    """A short type hint for an assignment target."""
    if isinstance(value, ast.Constant):
        return type(value.value).__name__
    if isinstance(value, ast.JoinedStr):
        return "str"
    if isinstance(value, ast.List | ast.ListComp):
        return "list"
    if isinstance(value, ast.Dict | ast.DictComp):
        return "dict"
    if isinstance(value, ast.Set | ast.SetComp):
        return "set"
    if isinstance(value, ast.Tuple):
        return "tuple"
    if isinstance(value, ast.Call):
        func = value.func
        if isinstance(func, ast.Name):
            return func.id
        if isinstance(func, ast.Attribute):
            return func.attr
    if isinstance(value, ast.BinOp):
        return _describe_value(value.left)
    return ""


def _describe_annotation(node: ast.AST | None) -> str:
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return ""

class PyTextArea(TextArea):
    """TextArea coloured by Pygments instead of tree-sitter.

    tree-sitter grammars are not always installable (on Termux the python
    binding fails to load), and TextArea raises at construction time when the
    language is missing. Pygments is already a Textual dependency, so the
    highlighting is driven from its token stream instead.
    """

    def __init__(self, text: str, **kwargs) -> None:
        super().__init__(text, language=None, **kwargs)
        self._line_cache.clear()
        self._menu: "CompletionMenu | None" = None
        self._index = SymbolIndex(text)
        self._word = ""
        self._prefix = ""          # the expression the popup is describing
        self._attribute = False    # True while completing after a dot
        self._signature = ""       # the parameter hint, when inside a call
        self._signature_params: tuple[str, ...] = ()
        self._signature_index = 0

    # -- IntelliSense ---------------------------------------------------
    @property
    def menu(self) -> "CompletionMenu":
        """The popup, mounted once on the screen the first time it is needed."""
        if self._menu is None:
            self._menu = CompletionMenu(id="completion-menu")
            self.screen.mount(self._menu)
        return self._menu

    def reindex(self) -> None:
        """Re-read the file's symbols. Called whenever the text settles."""
        self._index = SymbolIndex(self.text)

    def _completion_context(self) -> tuple[str, str]:
        """Split the text before the caret into (expression, partial word).

        `items.ap` -> ("items", "ap")   so members of `items` are offered.
        `pri`      -> ("", "pri")       so the file's names are offered.
        """
        row, column = self.cursor_location
        line = self.document.get_line(row)[:column]
        match = re.search(r"[A-Za-z0-9_]*$", line)
        partial = match.group(0) if match else ""
        before = line[: match.start()] if match else line
        if before.endswith("."):
            # `items.ap` -> ("items", "ap"); `items.` -> ("items", "")
            head = re.search(r"[A-Za-z_][A-Za-z0-9_.]*$", before[:-1])
            return (head.group(0) if head else ""), partial
        return "", partial

    def _place_menu(self) -> None:
        """Put the popup where VS Code would: under the caret, or above it.

        The height is whatever space is actually left in the terminal, so the
        list can never spill over the terminal pane or the buttons below the
        editor. If neither side has room, it shrinks rather than covering the
        interface.
        """
        menu = self.menu
        if not menu.matches:
            return
        row, column = self.cursor_location
        offset = self.scroll_offset
        gutter = self.gutter_width

        screen = self.screen.region
        caret_x = self.region.x + gutter + column - offset.x
        caret_y = self.region.y + row - offset.y

        # Sit beside the caret, not on top of it: the code being typed stays
        # readable while the list is open. Only fall back to below/above when
        # there is no room to the right.
        chrome = 3
        gap = 2
        right_x = caret_x + gap
        width = min(44, screen.right - right_x - 1)
        beside = width >= 16

        # Prefer to stay inside the editor, so the list never climbs over the
        # lesson pane or the top bar. On a very short editor that leaves no
        # room at all, so fall back to the whole screen — the popup is to the
        # right of the caret either way, so the line being typed stays visible.
        panel_top, panel_bottom = self.region.y, self.region.bottom
        space_below = max(0, panel_bottom - (caret_y + 1))
        space_above = max(0, caret_y - panel_top)
        if max(space_below, space_above) < 4:
            # never above the top bar, never over the bottom bar
            panel_top = screen.y + 7
            try:
                panel_top = self.app.query_one("#topbar").region.bottom
            except Exception:
                pass
            panel_bottom = screen.bottom - 4
            space_below = max(0, panel_bottom - (caret_y + 1))
            space_above = max(0, caret_y - panel_top)

        if beside:
            # The caret can be near the bottom of the pane while the pane has
            # plenty of room above the line: measure from the pane edges, not
            # from the caret, or a 3-row popup appears in a 20-row editor.
            upward = space_above > space_below
            if upward:
                available = space_above
                anchor_y = caret_y
            else:
                # grow upward from the pane bottom so the full height is used
                available = max(space_below, panel_bottom - panel_top)
                anchor_y = panel_bottom if space_below < 4 else caret_y + 1
            x = right_x
        else:
            available = space_below if space_below >= space_above else space_above
            upward = space_above > space_below
            anchor_y = caret_y if upward else caret_y + 1
            width = min(44, max(18, self.size.width))
            x = caret_x

        rows = max(1, min(len(menu.matches), available - chrome))
        menu.set_rows(rows)
        height = min(len(menu.visible()), rows) + chrome

        x = max(screen.x, min(x, screen.right - width))
        y = anchor_y - height if upward else anchor_y
        y = max(screen.y, min(y, screen.bottom - height))
        menu.styles.offset = (x - screen.x, y - screen.y)

    def refresh_completions(self, *, force: bool = False) -> None:
        """Decide what the popup should show for the caret's position."""
        # Re-read the source here rather than relying on the keystroke hook:
        # the index must reflect the document as it is *now*, including text
        # set programmatically or pasted in one go.
        if self._index.source != self.text:
            self.reindex()
        expr, partial = self._completion_context()
        self._prefix, self._word = expr, partial
        self._attribute = bool(expr)

        if expr:
            matches = self._index.members_of(expr)
            if partial:
                matches = [c for c in matches if c.label.startswith(partial)]
        else:
            if not partial and not force:
                self.menu.hide()
                return
            matches = self._index.suggest(partial)

        # A row identical to what is already typed does nothing when picked,
        # so drop it: `import pri` must not offer `pri` back.
        matches = [c for c in matches if c.label != partial]

        if not matches:
            self.menu.hide()
            return
        self.menu.show(matches, 0)
        self._place_menu()

    def _in_no_parens_context(self) -> bool:
        """Where Pylance deliberately skips the parentheses.

        Inside an `import`, a type annotation or a decorator a call is not
        what is wanted, so `print` there stays `print`.
        """
        row, column = self.cursor_location
        line = self.document.get_line(row)
        if line.lstrip().startswith(("import ", "from ")):
            return True
        if line.lstrip().startswith("@"):
            return True
        # An annotation, not a call. Checked from the start of the line so it
        # still matches while the word itself is being completed: the text
        # before the caret is `x: pri`, and `pri` has not been replaced yet.
        before = line[:column]
        if re.search(r":\s*[A-Za-z_][A-Za-z0-9_.]*$", before):
            return True
        # `def f(x: int)` — the annotation sits inside the def's parentheses
        return bool(re.match(r"\s*def\s+\w+\s*\([^)]*:\s*[A-Za-z_.]*$", line))

    def apply_completion(self) -> None:
        completion = self.menu.current()
        if completion is None:
            return
        row, column = self.cursor_location
        # decide *before* removing the typed word: the annotation check needs
        # to see `x: pri`, and after the delete it would only see `x: `
        wants_parens = completion.callable and not self._in_no_parens_context()
        self.delete((row, column - len(self._word)), (row, column))

        # `print` becomes `print(|)` — cursor between the parens, ready for
        # arguments, exactly like completeFunctionParens in Pylance.
        if wants_parens:
            self.insert(f"{completion.label}()")
            self.move_cursor((row, column - len(self._word) + len(completion.label) + 1))
        else:
            self.insert(completion.label)
        self.menu.hide()
        self._signature = ""
        self._signature_index = 0
        self.refresh_signature()

    def move_suggestion(self, delta: int) -> None:
        menu = self.menu
        menu.show(menu.matches, (menu.index + delta) % len(menu.matches))
        self._place_menu()

    # -- signature help -------------------------------------------------
    def _call_under_cursor(self) -> tuple[str, int] | None:
        """The call the caret sits inside, and which argument it is on.

        Returns `("print", 0)` while typing the first argument of `print(`.
        Scanning is done by hand because the document is usually not valid
        Python yet — `print(` on its own is a syntax error.
        """
        row, column = self.cursor_location
        line = self.document.get_line(row)[:column]
        depth = 0
        index = 0
        for position in range(len(line) - 1, -1, -1):
            char = line[position]
            if char in ")]}":
                depth += 1
            elif char in "([{":
                if depth == 0:
                    if char != "(":
                        return None
                    head = re.search(r"([A-Za-z_][A-Za-z0-9_.]*)\s*$", line[:position])
                    if not head:
                        return None
                    return head.group(1), index
                depth -= 1
            elif char == "," and depth == 0:
                index += 1
        return None

    def refresh_signature(self) -> None:
        """Show the parameters of the call the caret is in."""
        call = self._call_under_cursor()
        if call is None:
            self._signature = ""
            try:
                self.app.query_one("#signature", SignatureHint).hide()
            except Exception:
                pass
            return
        name, index = call
        params = self._index.signatures.get(name)
        if params is None:
            params = _BUILTIN_SIGNATURES.get(name)
        if not params:
            self._signature = ""
            return
        self._signature = f"{name}({', '.join(params)})"
        self._signature_index = min(index, len(params) - 1)
        self._signature_params = params
        try:
            self.app.query_one("#signature", SignatureHint).show(
                self._signature, params, self._signature_index
            )
        except Exception:
            pass

    # -- events ---------------------------------------------------------
    async def _on_key(self, event) -> None:
        menu = self._menu
        if menu is not None and menu.open:
            key = event.key
            if key == "down":
                event.stop()
                event.prevent_default()
                self.move_suggestion(1)
                return
            if key == "up":
                event.stop()
                event.prevent_default()
                self.move_suggestion(-1)
                return
            if key in ("tab", "enter"):
                event.stop()
                event.prevent_default()
                self.apply_completion()
                return
            if key == "escape":
                event.stop()
                event.prevent_default()
                menu.hide()
                return
        if event.key == "ctrl+space":
            event.stop()
            event.prevent_default()
            self.reindex()
            self.refresh_completions(force=True)
            return
        await super()._on_key(event)
        self.reindex()
        self.refresh_completions()
        self.refresh_signature()

    def on_blur(self) -> None:
        if self._menu is not None:
            self._menu.hide()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area is self:
            self.reindex()

    def _build_highlight_map(self) -> None:
        self._line_cache.clear()
        highlights: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
        self._highlights = highlights

        text = self.text
        lines = text.split("\n")

        def to_bytes(row: int, column: int) -> int:
            """TextArea looks highlights up by UTF-8 byte offset, but Pygments
            reports codepoint offsets — a line holding an emoji would shift."""
            if not 0 <= row < len(lines):
                return column
            return len(lines[row][:column].encode("utf-8"))

        for index, ttype, value in PythonLexer(stripnl=False).get_tokens_unprocessed(text):
            if not value.strip():
                continue
            row = text.count("\n", 0, index)
            column = index - (text.rfind("\n", 0, index) + 1)
            role = _token_role(ttype)
            for offset, part in enumerate(value.split("\n")):
                if part.strip():
                    start = column if offset == 0 else 0
                    line = row + offset
                    begin = to_bytes(line, start)
                    end = to_bytes(line, start + len(part))
                    highlights[line].append((begin, end, role))
                column = 0


def _token_role(ttype) -> str:
    if ttype in Token.Comment:
        return "comment"
    if ttype in Token.Literal.String:
        return "string"
    if ttype in Token.Name.Builtin or ttype in Token.Name.Function:
        return "function.builtin"
    if ttype in Token.Keyword:
        return "keyword"
    if ttype in Token.Literal.Number:
        return "number"
    return ""


class SignatureHint(Static):
    """The parameter hint that sits under the caret while inside a call."""

    DEFAULT_CSS = """
    SignatureHint {
        height: 1;
        width: 100%;
        padding: 0 1;
        background: #16233d;
        color: #94a3bd;
        display: none;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self.signature = ""
        self.params: tuple[str, ...] = ()
        self.index = 0

    def show(self, signature: str, params: tuple[str, ...], index: int) -> None:
        self.signature = signature
        self.params = params
        self.index = index
        self.display = True
        self.refresh()

    def hide(self) -> None:
        self.signature = ""
        self.display = False

    def render(self) -> Text:
        text = Text(no_wrap=True)
        text.append("ƒ ", Style(color=GREEN, bold=True))
        text.append(self.signature, Style(color=MUTED))
        if self.params:
            active = self.params[min(self.index, len(self.params) - 1)]
            text.append("   ▸ ", Style(color=GREEN))
            text.append(active, Style(color=GREEN, bold=True))
            text.append(f"  ({self.index + 1}/{len(self.params)})",
                        Style(color=MUTED))
        return text


class CompletionMenu(Static):
    """Completion popup that behaves like the one in VS Code.

    It shows as many rows as the space around the caret allows and scrolls
    through the rest, instead of drawing a fixed block over the interface.
    """

    DEFAULT_CSS = """
    CompletionMenu {
        layer: overlay;
        width: auto;
        max-width: 44;
        height: auto;
        background: #1b2436;
        border: round #3b4a6b;
        padding: 0 1;
        display: none;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("", **kwargs)
        self.matches: list[Completion] = []
        self.index = 0
        self.view = 0          # first visible row
        self.rows = 8          # how many rows fit right now

    # -- content --------------------------------------------------------
    def show(self, matches: list[Completion], index: int = 0) -> None:
        self.matches = matches
        self.index = max(0, min(index, len(matches) - 1))
        self.display = bool(matches)
        self._clamp_view()
        self.refresh(layout=True)

    def hide(self) -> None:
        self.matches = []
        self.display = False

    @property
    def open(self) -> bool:
        return bool(self.matches)

    def current(self) -> "Completion | None":
        return self.matches[self.index] if self.matches else None

    def set_rows(self, rows: int) -> None:
        """How many rows fit; called when the popup is placed."""
        self.rows = max(1, min(rows, len(self.matches) or 1))
        self._clamp_view()
        self.refresh(layout=True)

    def _clamp_view(self) -> None:
        """Keep the selected row inside the visible window."""
        if self.index < self.view:
            self.view = self.index
        elif self.index >= self.view + self.rows:
            self.view = self.index - self.rows + 1
        self.view = max(0, min(self.view, max(0, len(self.matches) - self.rows)))

    def visible(self) -> list[Completion]:
        return self.matches[self.view:self.view + self.rows]

    def render(self) -> Text:
        text = Text(no_wrap=True)
        rows = self.visible()
        width = max((len(c.label) for c in rows), default=8)
        width = min(width, 18)
        for offset, completion in enumerate(rows):
            row = self.view + offset
            selected = row == self.index
            text.append("▸ " if selected else "  ",
                        Style(color=GREEN, bold=True))
            text.append(f"{completion.icon} ",
                        Style(color=GREEN if selected else MUTED))
            text.append(f"{completion.label:<{width}}",
                        Style(color=GREEN if selected else TEXT, bold=selected))
            if completion.detail:
                text.append("  ", Style())
                text.append(completion.detail, Style(color=MUTED))
            if offset < len(rows) - 1:
                text.append("\n")
        # a scrollbar on the right, the way VS Code hints at more rows
        if len(self.matches) > self.rows:
            first = self.view + 1
            last = min(self.view + self.rows, len(self.matches))
            text.append(f"  {first}-{last}/{len(self.matches)}", Style(color=MUTED))
        return text


class PixelButton(Button):
    """Square button with a hard 'shadow' on the bottom/right edge."""


# --------------------------------------------------------------------------- #
#  Main menu — an animated night city behind a block-letter title
# --------------------------------------------------------------------------- #
#
# The whole scene is painted by ONE widget. Textual has no per-widget alpha
# blending: a child with `background: transparent` still paints the app
# background over its parent, so a title in a separate widget would punch a
# hole in the skyline. Drawing sky, city, rain and title into the same cell
# grid keeps them composited together.
#
# Half blocks give 2 vertical pixels per text row, so the city has real
# detail without the rows looking stretched.

TITLE_BLOCK = {
    "p": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "y": ("#...#", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    "l": ("##...", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "e": (".###.", "#...#", "#####", "#....", "#....", "#...#", ".###."),
    "a": (".###.", "#...#", "#...#", ".####", "....#", "#...#", ".###."),
    "r": ("#.##.", "##..#", "#....", "#....", "#....", "#....", "#...."),
    "n": ("#.##.", "##..#", "#...#", "#...#", "#...#", "#...#", "#...#"),
}
TITLE_WORD = "pylearn"
TITLE_GAP = 4          # blank columns between letters
TITLE_TO_BUTTON = 3    # blank rows between the title and the Start button
BUTTON_ROWS = 3        # PixelButton height


def _title_rows() -> list[str]:
    """Expand the block letters into rows of "1"/"0" strings.

    Every glyph is padded to the widest one, so a narrow letter cannot shift
    the rows out of alignment.
    """
    letters = [TITLE_BLOCK[ch] for ch in TITLE_WORD]
    width = max(len(row) for letter in letters for row in letter)
    height = max(len(letter) for letter in letters)
    rows: list[str] = []
    for row in range(height):
        parts = []
        for letter in letters:
            line = letter[row] if row < len(letter) else ""
            parts.append(line.ljust(width, "."))
        rows.append(("." * TITLE_GAP).join(parts))
    return rows


def _mix(a: str, b: str, t: float) -> str:
    """Blend two hex colours; t=0 gives a, t=1 gives b."""
    t = max(0.0, min(1.0, t))
    ca = [int(a.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


# --------------------------------------------------------------------------- #
#  Course path — modules and their levels
# --------------------------------------------------------------------------- #


@dataclass
class Level:
    number: int
    title: str
    state: str = "locked"      # "done" | "unlocked" | "locked"
    note: str = ""
    exercise: int = 0          # global exercise number across the course
    lesson: object = None      # lessons.Level — the content for this level


@dataclass
class Module:
    number: int
    title: str
    blurb: str
    levels: list[Level]
    open: bool = False


LESSON_DIR = "lessons"

PROGRESS_FILE = Path(__file__).resolve().with_name("pylearn_progress.json")
"""Where level state and hint counts are kept between runs."""

PROGRESS_VERSION = 1

#: How an answer is judged. A lesson declares one in its frontmatter:
#:
#:   check: output   compare stdout with `expect` — the default
#:   check: strict   the same, and the program must also exit cleanly
#:
#: `reseed` (re-roll the level and run the answer again) was tried and
#: removed. Every lesson states its numbers on screen, so the reference
#: solution itself is written with those literals — re-rolling rejected the
#: correct answer. Guarding against a copied number needs lessons that take a
#: value from somewhere other than the text, which is a rewrite of the
#: material, not a checker setting.
CHECK_MODES = ("output", "strict")

# --------------------------------------------------------------------------- #
#  Progress — what survives a restart
# --------------------------------------------------------------------------- #
#
# Only level STATE is stored, keyed by the lesson slug (`01-02-hello-world`),
# never by level number: inserting a lesson file in the middle would shift
# every number and corrupt someone's saved progress.
#
# The rolled values of a level are deliberately NOT stored. `_load_level()`
# re-rolls on every visit, which is what stops the answer being memorised.


def load_progress() -> dict:
    """Read the save file, tolerating anything that is not valid.

    A corrupt or half-written file must not stop the app from starting, so any
    problem falls back to an empty progress rather than raising.
    """
    try:
        raw = PROGRESS_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (FileNotFoundError, OSError, ValueError):
        return {"version": PROGRESS_VERSION, "levels": {}}
    if not isinstance(data, dict):
        return {"version": PROGRESS_VERSION, "levels": {}}
    levels = data.get("levels")
    return {
        "version": PROGRESS_VERSION,
        "levels": levels if isinstance(levels, dict) else {},
    }


def save_progress(data: dict) -> None:
    """Write the save file atomically, so a crash cannot truncate it."""
    tmp = PROGRESS_FILE.with_suffix(".json.tmp")
    try:
        tmp.write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
        tmp.replace(PROGRESS_FILE)
    except OSError as exc:
        print(f"pylearn: could not save progress ({exc})", file=sys.stderr)


def apply_progress(modules: list, data: dict) -> None:
    """Merge saved state into the freshly loaded course.

    A level counts as unlocked when the one before it is done, so unlocking is
    derived from the data instead of stored twice.
    """
    saved = data.get("levels", {})
    previous_done = True          # the first level is always open
    for module in modules:
        for level in module.levels:
            slug = getattr(level.lesson, "slug", "")
            entry = saved.get(slug, {})
            if entry.get("done"):
                level.state = "done"
            elif previous_done:
                level.state = "unlocked"
            else:
                level.state = "locked"
            previous_done = level.state == "done"


def unlock_next(modules: list, done_level) -> None:
    """Open the level that follows `done_level` in course order.

    States were only ever derived at load time, so finishing a level left the
    next one locked until the app was restarted.
    """
    flat = [lv for module in modules for lv in module.levels]
    try:
        index = flat.index(done_level)
    except ValueError:
        return
    if index + 1 < len(flat):
        nxt = flat[index + 1]
        if nxt.state == "locked":
            nxt.state = "unlocked"


def collect_progress(app) -> dict:
    """Build the save payload from the live app state."""
    levels = {}
    for module in app.modules:
        for level in module.levels:
            slug = getattr(level.lesson, "slug", "")
            failures = app.failures.get(slug, 0)
            if level.state == "done" or failures:
                levels[slug] = {
                    "done": level.state == "done",
                    "failures": failures,
                }
    return {"version": PROGRESS_VERSION, "levels": levels}


HINT_AFTER = 3
"""Wrong submissions before the Hint row unlocks."""

SOLUTION_AFTER = 6
"""Wrong submissions before the Solution row unlocks."""


def _build_modules() -> list[Module]:
    """Load the course from `lessons/` and attach progress state.

    Progress is still in-memory: the first level is done, the next is open,
    everything after is locked. Persisting it is a separate job.
    """
    from lessons import load_course

    modules: list[Module] = []
    for source in load_course(LESSON_DIR):
        levels = []
        for lesson in source.levels:
            # provisional; apply_progress() derives the real state from the
            # save file, and the first level is open because nothing precedes it
            state = "locked"
            levels.append(
                Level(
                    number=lesson.order,
                    title=lesson.title,
                    state=state,
                    note=lesson.hint,
                    exercise=lesson.exercise,
                    lesson=lesson,
                )
            )
        modules.append(Module(source.number, source.title, source.blurb, levels))
    return modules


def _build_modules_hardcoded() -> list[Module]:
    return [
        Module(
            1, "Setting Up",
            "Install Python, meet the editor, and print your very first line. "
            "Nothing to install here — the editor is built in.",
            [
                Level(1, "Hello World", 10, "done"),
                Level(2, "Print Statements", 10, "done"),
                Level(3, "Variables", 15, "unlocked",
                      "Store a value in a name and print it back."),
                Level(4, "Data Types", 15, "locked"),
                Level(5, "Input & Output", 20, "locked"),
            ],
        ),
        Module(
            2, "Control Flow",
            "Make the computer choose. Conditions, comparisons, and the "
            "if / elif / else ladder.",
            [
                Level(1, "Booleans", 15, "locked"),
                Level(2, "If Statements", 20, "locked"),
                Level(3, "Else & Elif", 20, "locked"),
                Level(4, "While Loops", 25, "locked"),
            ],
        ),
        Module(
            3, "Collections",
            "Group values together: lists, tuples, dictionaries and sets, "
            "and the loops that walk them.",
            [
                Level(1, "Lists", 20, "locked"),
                Level(2, "Tuples", 20, "locked"),
                Level(3, "Dictionaries", 25, "locked"),
                Level(4, "Sets", 25, "locked"),
            ],
        ),
    ]


LEVEL_ICON = {"done": "✓", "unlocked": "▶", "locked": "▣"}
"""ASCII-safe markers. `⚿` measures as one cell but renders as two in many
terminals, which silently clipped the button label."""
"""Single-cell glyphs: the padlock emoji is two cells wide and would shift
every row it sits in."""


# --------------------------------------------------------------------------- #
#  Main menu — an animated pixel-art beach behind a block-letter title
# --------------------------------------------------------------------------- #
#
# The scene is drawn into a pixel buffer of `width x height*2` and then packed
# two pixels per text cell with "▀" (foreground = top pixel, background =
# bottom pixel). Half blocks double the vertical resolution, which is what
# makes pixel art read properly in a terminal.
#
# Everything is painted by ONE widget on purpose: Textual has no per-widget
# alpha, so a title in a sibling widget would paint the app background over
# the sky. One canvas keeps sky, sea, palms and title composited together.

BEACH = {
    "sky_top": "#1a6ec6",
    "sky_mid": "#4aa3e8",
    "sky_low": "#b6e4f7",
    "sun": "#fff8d0",
    "sun_glow": "#ffe98a",
    "cloud": "#ffffff",
    "cloud_shade": "#d6ebfa",
    "cloud_deep": "#b3d6f0",
    "sea_far": "#2f93cf",
    "sea_mid": "#1f7cbb",
    "sea_near": "#4cc0dd",
    "foam": "#f4fcff",
    "sand": "#f6e6bd",
    "sand_wet": "#e3cb97",
    "sand_dark": "#cdb27c",
    "trunk": "#8a5a34",
    "trunk_dark": "#67401f",
    "frond": "#2f9e44",
    "frond_dark": "#1c7530",
    "frond_light": "#5cc46a",
    "coconut": "#5a3a1e",
    "title_outline": "#0a2540",
    "title_shadow": "#123a5e",
    "title_face": "#12324f",
    "btn_yellow": "#ffe14d",
    "btn_shadow": "#6b4f00",
    "title_top": "#fff6d5",
    "title_bottom": "#ffc94d",
}

_PAIR_CACHE: dict[tuple[str, str], Style] = {}


def _pair(top: str, bottom: str) -> Style:
    """Style for one half-block cell, cached: hundreds are built per frame."""
    key = (top, bottom)
    style = _PAIR_CACHE.get(key)
    if style is None:
        style = Style(color=top, bgcolor=bottom)
        _PAIR_CACHE[key] = style
    return style


BTN_FONT = {
    "S": ("#####", "#....", "####.", "....#", "#####"),
    "t": ("..#..", ".###.", "..#..", "..#..", "..##."),
    "a": (".###.", "....#", ".####", "#...#", ".####"),
    "r": ("##...", "#.#..", "#..##", "#....", "#...."),
}
BTN_ADVANCE = 6
"""Columns per glyph, including the gap after it."""


def _put_glyph(buf: list[list[str]], x: int, y: int, char: str, color: str) -> None:
    """Draw one character from BTN_FONT, centred vertically on `y`."""
    rows = BTN_FONT.get(char)
    if rows is None:
        return
    start = y - len(rows) // 2
    for dy, row in enumerate(rows):
        for dx, bit in enumerate(row):
            if bit == "#":
                _put(buf, x + dx, start + dy, color)


def _put(buf: list[list[str]], x: int, y: int, color: str) -> None:
    if 0 <= y < len(buf) and 0 <= x < len(buf[0]):
        buf[y][x] = color


def _disc(buf: list[list[str]], cx: int, cy: int, radius: float, color: str) -> None:
    r2 = radius * radius
    for dy in range(-int(radius), int(radius) + 1):
        for dx in range(-int(radius), int(radius) + 1):
            if dx * dx + dy * dy <= r2:
                _put(buf, cx + dx, cy + dy, color)


def _blob(buf: list[list[str]], cx: int, cy: int, rx: float, ry: float, color: str) -> None:
    """Filled ellipse — clouds and palm fronds are built from these."""
    if rx < 0.5 or ry < 0.5:
        return
    for dy in range(-int(ry), int(ry) + 1):
        for dx in range(-int(rx), int(rx) + 1):
            if (dx / rx) ** 2 + (dy / ry) ** 2 <= 1.0:
                _put(buf, cx + dx, cy + dy, color)


class Beach(Widget):
    """Sky, sun, clouds, sea, surf, sand and palms — plus the block title.

    The frame counter drives the surf and the drifting clouds; everything else
    is derived from the widget size, so a resize re-lays the scene cleanly.
    """

    DEFAULT_CSS = """
    Beach {
        width: 1fr;
        height: 1fr;
        background: #1a6ec6;
    }
    Beach:focus { background-tint: transparent; }
    """


    FPS = 12
    """Surf and clouds read fine at 12 fps; more just burns CPU in Termux."""

    def __init__(self, seed: int = 7, **kwargs) -> None:
        super().__init__(**kwargs)
        self._seed = seed
        self._frame = 0
        self._timer = None
        self._title = _title_rows()
        self._title_w = len(self._title[0])
        self._title_h = len(self._title)
        self._cache: list[list[str]] | None = None
        self._cache_key: tuple[int, int, int] | None = None

    # -- lifecycle ---------------------------------------------------------

    def on_mount(self) -> None:
        self._timer = self.set_interval(1 / self.FPS, self._tick)
        self.call_after_refresh(self.sync_button_fill)

    def on_unmount(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

    def _tick(self) -> None:
        self._frame += 1
        self.refresh()
        self.call_after_refresh(self.sync_button_fill)

    def set_animated(self, animate: bool) -> None:
        """Turn the timer on or off; a still frame keeps the last pose."""
        if animate and self._timer is None:
            self._timer = self.set_interval(1 / self.FPS, self._tick)
        elif not animate and self._timer is not None:
            self._timer.stop()
            self._timer = None

    # -- scene pieces ------------------------------------------------------

    def _cloud(self, buf, cx: int, cy: int, scale: float) -> None:
        """One cumulus: a bumpy top over a flat base, shaded underneath."""
        r = 7.0 * scale
        puffs = (
            (0.0, 0.0, 1.00),
            (-1.15, 0.22, 0.80),
            (1.15, 0.26, 0.86),
            (-0.55, -0.52, 0.78),
            (0.62, -0.46, 0.72),
            (-1.95, 0.55, 0.58),
            (1.95, 0.58, 0.62),
            (0.10, -0.92, 0.62),
        )
        # shadow pass sits a couple of pixels lower
        for px, py, pr in puffs:
            _blob(buf, int(cx + px * r), int(cy + py * r) + 2,
                  pr * r, pr * r * 0.92, BEACH["cloud_deep"])
        _blob(buf, int(cx), int(cy + r * 0.55), r * 2.4, r * 0.55, BEACH["cloud_deep"])
        # body
        for px, py, pr in puffs:
            _blob(buf, int(cx + px * r), int(cy + py * r),
                  pr * r, pr * r * 0.92, BEACH["cloud"])
        _blob(buf, int(cx), int(cy + r * 0.5), r * 2.3, r * 0.5, BEACH["cloud"])
        # cool underside so it does not read as a flat sticker
        for px, py, pr in puffs:
            _blob(buf, int(cx + px * r), int(cy + py * r + pr * r * 0.62),
                  pr * r * 0.82, pr * r * 0.30, BEACH["cloud_shade"])

    def _palm(self, buf, base_x: int, base_y: int, top_y: int, lean: int,
              scale: float, width: int) -> None:
        """A palm: curved trunk, fan of fronds, a couple of coconuts."""
        span = base_y - top_y
        if span <= 4:
            return
        crown_x = base_x + lean
        # trunk — quadratic curve, wide at the base and tapering upward
        for step in range(span + 1):
            t = step / span
            x = int(base_x + (crown_x - base_x) * (t ** 1.6))
            y = base_y - step
            thick = max(1, int(round(4 - 2.6 * t)))
            for k in range(thick):
                shade = BEACH["trunk"] if k < thick - 1 else BEACH["trunk_dark"]
                _put(buf, x + k, y, shade)
        # fronds fan upward and outward
        angles = (-176, -156, -136, -116, -96, -76, -56, -36, -16)
        length = max(7, int(12 * scale))
        for angle in angles:
            rad = math.radians(angle)
            for step in range(1, length + 1):
                t = step / length
                fx = int(crown_x + math.cos(rad) * length * t)
                fy = int(top_y + math.sin(rad) * length * t + (t ** 2) * length * 0.50)
                # fronds are thick near the crown, tapering to a point
                thickness = max(1, int(round(3 - 2.2 * t)))
                for k in range(thickness):
                    _put(buf, fx, fy + k,
                         BEACH["frond"] if k == 0 else BEACH["frond_dark"])
                # a light ridge on top catches the sun
                if step % 2 == 0:
                    _put(buf, fx, fy - 1, BEACH["frond_light"])
        # crown + coconuts
        _blob(buf, crown_x, top_y, 2.2 * scale, 1.8 * scale, BEACH["frond_dark"])
        _disc(buf, crown_x - 2, top_y + 1, 1.2, BEACH["coconut"])
        _disc(buf, crown_x + 2, top_y + 1, 1.2, BEACH["coconut"])

    # -- buffer ------------------------------------------------------------

    def _build(self, width: int, height: int) -> list[list[str]]:
        px_w, px_h = width, height * 2
        frame = self._frame

        horizon = max(4, int(px_h * 0.56))
        shore = max(horizon + 3, int(px_h * 0.80))

        buf = [[BEACH["sky_top"]] * px_w for _ in range(px_h)]

        # sky gradient, two stops so the horizon glows
        for y in range(horizon):
            t = y / max(1, horizon - 1)
            colour = (_mix(BEACH["sky_top"], BEACH["sky_mid"], t * 2)
                      if t < 0.5
                      else _mix(BEACH["sky_mid"], BEACH["sky_low"], (t - 0.5) * 2))
            row = buf[y]
            for x in range(px_w):
                row[x] = colour

        # sun with a soft halo
        sun_x, sun_y = int(px_w * 0.76), int(horizon * 0.26)
        sun_r = max(3.0, px_w / 34)
        _disc(buf, sun_x, sun_y, sun_r + 2.5, BEACH["sun_glow"])
        _disc(buf, sun_x, sun_y, sun_r, BEACH["sun"])

        # clouds drift slowly and wrap around the edges
        # clouds stay low enough that none of them drifts behind the title
        for (fx, fy, scale, speed) in (
            (0.20, 0.34, 1.00, 0.20),
            (0.56, 0.26, 0.72, 0.13),
            (0.88, 0.40, 0.85, 0.16),
        ):
            drift = (frame * speed) % (px_w + 90)
            cx = int(fx * px_w + drift) - 45
            self._cloud(buf, cx, int(horizon * fy), scale)

        # sea, then sand below a wavy shoreline
        edge = [shore + int(2.2 * math.sin(x * 0.075 + frame * 0.20))
                for x in range(px_w)]
        for y in range(horizon, px_h):
            row = buf[y]
            for x in range(px_w):
                if y < edge[x]:
                    t = (y - horizon) / max(1, shore - horizon)
                    row[x] = _mix(BEACH["sea_far"], BEACH["sea_near"], t)
                else:
                    t = (y - edge[x]) / max(1, px_h - edge[x])
                    row[x] = _mix(BEACH["sand_wet"], BEACH["sand"], min(1.0, t * 1.6))

        # rolling surf: two foam lines chasing the shore
        for x in range(px_w):
            for offset, phase in ((0, 0.0), (4, 2.4)):
                wave = int(1.4 * math.sin(x * 0.11 + frame * 0.22 - phase))
                fy = edge[x] - 5 - offset + wave
                if horizon <= fy < px_h:
                    _put(buf, x, fy, BEACH["foam"])
                    # a thin shadow just under the crest keeps it from
                    # reading as a solid white band
                    if offset and (x + frame) % 7 < 4:
                        _put(buf, x, fy + 1, BEACH["sea_near"])
            _put(buf, x, edge[x], BEACH["foam"])

        # sunlight glittering on the water
        for x in range(2, px_w, 9):
            y = horizon + 3 + ((x * 7 + frame * 3) % max(1, shore - horizon - 6))
            if (x + frame) % 13 < 5:
                _put(buf, x, y, BEACH["foam"])
                _put(buf, x + 1, y, BEACH["foam"])

        # palms frame the scene; skip them when the terminal is too narrow
        if px_w >= 70:
            scale = 1.0 if px_w >= 100 else 0.78
            ground = min(px_h - 2, shore + 4)
            self._palm(buf, int(px_w * 0.07), ground,
                       int(horizon * 0.46), int(px_w * 0.030), scale, px_w)
            self._palm(buf, int(px_w * 0.93), ground,
                       int(horizon * 0.40), -int(px_w * 0.034), scale, px_w)

        self._paint_title(buf, px_w, px_h, height)
        return buf

    TITLE_SCALE = 1
    """Each font pixel is one terminal pixel (two per text row). At 2x the word
    was 82 columns wide and dominated the scene; at 1x it is 41 and reads as a
    title rather than a billboard."""

    def _paint_title(self, buf, px_w: int, px_h: int, height_rows: int) -> None:
        """Block letters in the upper sky, over a soft plate."""
        scale = self.TITLE_SCALE
        title_w = self._title_w * scale
        title_h = self._title_h * scale
        left = max(0, (px_w - title_w) // 2)

        # The title and the Start button are one centred group: the title,
        # a gap, then the 3-row button. Both are measured in text rows so the
        # group's centre lines up with the widget's centre.
        group_px = title_h + (TITLE_TO_BUTTON + BUTTON_ROWS) * 2
        top = max(2, (px_h - group_px) // 2)

        lit: set[tuple[int, int]] = set()
        for ty, line in enumerate(self._title):
            for tx, ch in enumerate(line):
                if ch != "#":
                    continue
                for dy in range(scale):
                    for dx in range(scale):
                        lit.add((left + tx * scale + dx, top + ty * scale + dy))

        # A 1px outline hugs the letters. A slab behind the word reads as a
        # floating rectangle in the middle of the sky, which is exactly the
        # stiffness this scene is trying to avoid.
        for (lx, ly) in lit:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (lx + dx, ly + dy) not in lit:
                        _put(buf, lx + dx, ly + dy, "#0a2540")

        for (lx, ly) in lit:
            t = (ly - top) / max(1, title_h - 1)
            _put(buf, lx, ly, _mix(BEACH["title_top"], BEACH["title_bottom"], t))

    def sync_button_fill(self) -> None:
        """Match the Start button's fill to the pixels behind it.

        Textual cannot blend a widget over its parent, so "transparent" has to
        mean "painted the same colour as the scene underneath". Sampling the
        buffer is the only way to get that right as the sky gradient shifts.
        """
        try:
            button = self.query_one("#start-btn", PixelButton)
        except Exception:
            return
        if self._cache is None:
            return
        rel = button.region - self.region.offset
        if rel.width <= 0 or rel.height <= 0:
            return
        # dominant colour under the button, not a single pixel: the sea has
        # foam lines, so one sample can land on white
        counts: dict[str, int] = {}
        for row in range(rel.y, rel.y + rel.height):
            for x in range(rel.x, rel.x + rel.width):
                for py in (row * 2, row * 2 + 1):
                    if 0 <= py < len(self._cache) and 0 <= x < len(self._cache[py]):
                        c = self._cache[py][x]
                        counts[c] = counts.get(c, 0) + 1
        if not counts:
            return
        colour = max(counts, key=counts.get)
        if button.styles.background != colour:
            button.styles.background = colour

    # -- render ------------------------------------------------------------

    def render_line(self, y: int) -> Strip:
        width, height = self.size
        if not width or not height:
            return Strip.blank(width)

        key = (width, height, self._frame)
        if self._cache_key != key:
            self._cache = self._build(width, height)
            self._cache_key = key
        buf = self._cache

        top_row = buf[y * 2]
        bot_row = buf[y * 2 + 1]
        segments: list[Segment] = []
        run: list[str] = []
        current: Style | None = None
        for x in range(width):
            t, b = top_row[x], bot_row[x]
            char = " " if t == b else "▀"
            style = _pair(t, b)
            if style is not current:
                if run:
                    segments.append(Segment("".join(run), current))
                run = []
                current = style
            run.append(char)
        if run:
            segments.append(Segment("".join(run), current))
        return Strip(segments, width)


_STYLE_CACHE: dict[tuple, Style] = {}


def _cell_style(fg: str | None = None, bg: str | None = None,
                bold: bool = False) -> Style:
    """One cached Style per (fg, bg, bold).

    Every cell in a row must carry the row's background. Leaving text cells
    with no bgcolor makes them sit on the pane colour while the padding sits
    on the highlight — which is what made the labels look like differently
    coloured boxes.
    """
    key = (fg, bg, bold)
    style = _STYLE_CACHE.get(key)
    if style is None:
        style = Style(color=fg, bgcolor=bg, bold=bold)
        _STYLE_CACHE[key] = style
    return style


def _strip_from_cells(cells: list[tuple[str, Style]], width: int) -> Strip:
    """Pack a cell list into a Strip, merging neighbours with the same style."""
    cells = cells[:width]
    pad = _cell_style()
    while len(cells) < width:
        cells.append((" ", pad))
    segments: list[Segment] = []
    run: list[str] = []
    current: Style | None = None
    for char, style in cells:
        if style is not current:
            if run:
                segments.append(Segment("".join(run), current))
            run = []
            current = style
        run.append(char)
    if run:
        segments.append(Segment("".join(run), current))
    return Strip(segments, width)


class LevelRow(Widget):
    """One row of the path: rail circle, level name, title, action.

    The rail is painted on every row — above and below the circle — so the
    line runs unbroken through the whole module. Every cell carries the row's
    background colour; text left on the pane colour reads as a stray box.
    """

    DEFAULT_CSS = """
    LevelRow { width: 1fr; height: 3; }
    """

    BG = "#0f1626"
    BG_SEL = "#1b2740"

    def __init__(self, level: Level, *, top: bool, bottom: bool,
                 selected: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.level = level
        self.top = top          # is there a circle above this one?
        self.bottom = bottom    # is there a circle below this one?
        self.selected = selected

    class Picked(Message):
        def __init__(self, level: Level) -> None:
            super().__init__()
            self.level = level

    def on_click(self) -> None:
        self.post_message(self.Picked(self.level))

    def render_line(self, y: int) -> Strip:
        width = self.size.width
        if not width:
            return Strip.blank(width)

        lv = self.level
        done = lv.state == "done"
        locked = lv.state == "locked"
        bg = self.BG_SEL if self.selected else self.BG

        circle_colour = (
            BEACH["frond"] if done
            else "#ffd166" if not locked
            else "#55688f"
        )
        ink = "#6a7694" if locked else TEXT

        cells: list[tuple[str, Style]] = [(" ", _cell_style(bg=bg)) for _ in range(width)]

        def put(col: int, chunk: str, style: Style) -> None:
            for offset, char in enumerate(chunk):
                pos = col + offset
                if 0 <= pos < width:
                    cells[pos] = (char, style)

        # rail: the circle, plus a connector only towards a real neighbour.
        # The first and last circles in the path get no stub above/below.
        if y == 1:
            glyph = "●" if not locked else "○"
            cells[0] = (glyph, _cell_style(circle_colour, bg, True))
        elif y == 0:
            cells[0] = ("│" if self.top else " ", _cell_style("#55688f", bg))
        else:
            cells[0] = ("│" if self.bottom else " ", _cell_style("#55688f", bg))

        if y != 1:
            return _strip_from_cells(cells, width)

        # level number, then the title
        put(2, f"Level {lv.number}", _cell_style(ink, bg))
        put(13, lv.title, _cell_style(ink, bg, not locked))

        if done:
            action, style = LEVEL_ICON["done"] + " done", _cell_style(BEACH["frond"], bg, True)
        elif locked:
            action, style = f"{LEVEL_ICON['locked']} locked", _cell_style("#6a7694", bg)
        else:
            action, style = f"{LEVEL_ICON['unlocked']} play", _cell_style("#ffd166", bg, True)

        put(max(18, width - len(action) - 2), action, style)
        return _strip_from_cells(cells, width)


class ModuleHead(Widget):
    """The module bar. It carries the same rail as the level rows, so the path
    stays continuous whether the module is open or closed."""

    DEFAULT_CSS = """
    ModuleHead { width: 1fr; height: 3; }
    """

    BG = "#161d30"

    def __init__(self, label: str, module: Module, *, top: bool, bottom: bool,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self._label = label
        self.module = module
        self.top = top
        self.bottom = bottom

    def on_click(self) -> None:
        self.post_message(ModuleCard.Toggled(self.module))

    def render_line(self, y: int) -> Strip:
        width = self.size.width
        if not width:
            return Strip.blank(width)

        bg = self.BG
        circle = "#ffd166" if self.module.open else "#55688f"
        cells: list[tuple[str, Style]] = [(" ", _cell_style(bg=bg)) for _ in range(width)]

        if y == 1:
            cells[0] = ("●", _cell_style(circle, bg, True))
            # label on the left, chevron flush right
            chevron = "⌃" if self.module.open else "⌄"
            label_style = _cell_style("#cdd7ea", bg, True)
            for offset, char in enumerate(self._label):
                pos = 2 + offset
                if pos < width:
                    cells[pos] = (char, label_style)
            if width >= 3:
                cells[width - 2] = (chevron, _cell_style("#94a3bd", bg))
        elif y == 0:
            cells[0] = ("│" if self.top else " ", _cell_style("#55688f", bg))
        else:
            cells[0] = ("│" if self.bottom else " ", _cell_style("#55688f", bg))

        return _strip_from_cells(cells, width)


class ModuleCard(Vertical):
    """A module: a header row that expands into its level rows.

    Closed, it is a single bar. Open, the bar stays put and the levels appear
    underneath it — the reference keeps the header visible so you always know
    which module the levels belong to.
    """

    def __init__(self, module: Module, selected_level: Level | None,
                 *, top: bool = False, bottom: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.module = module
        self._selected = selected_level
        self._top = top          # a circle exists above this module's dot
        self._bottom = bottom    # a circle exists below (next module / levels)
        self.styles.height = "auto"
        self.styles.width = "1fr"

    def compose(self) -> ComposeResult:
        levels = self.module.levels if self.module.open else []
        # A connector exists only between two circles that sit next to each
        # other: head <-> first level, level <-> level, head <-> next head.
        yield ModuleHead(
            self._header(), self.module,
            top=self._top,
            bottom=bool(levels) or self._bottom,
        )
        for index, level in enumerate(levels):
            yield LevelRow(
                level,
                top=index > 0,
                bottom=index < len(levels) - 1 or self._bottom,
                selected=(level is self._selected),
            )

    def _header(self) -> str:
        m = self.module
        return f"{m.number}. {m.title}"

    def on_click(self, event) -> None:
        head = event.widget
        if head is not None and head.has_class("module-head"):
            self.post_message(ModuleCard.Toggled(self))

    def on_level_row_picked(self, event: "LevelRow.Picked") -> None:
        # do NOT stop it: the screen above (PathScreen or Sidebar) decides
        # what a pick means
        self.post_message(ModuleCard.Picked(event.level))

    class Toggled(Message):
        def __init__(self, module: "Module") -> None:
            super().__init__()
            self.module = module

    class Picked(Message):
        """A level inside this card was clicked."""

        def __init__(self, level: "Level") -> None:
            super().__init__()
            self.level = level


class PathScreen(Vertical):
    """Module list on the left, the selected level on the right."""

    DEFAULT_CSS = """
    PathScreen {
        width: 1fr;
        height: 1fr;
        layout: horizontal;
        background: #0a0f1e;
    }
    #path-left {
        width: 52%;
        height: 1fr;
        padding: 1 1 1 0;
        border-right: thick #243049;
    }
    #path-right {
        width: 48%;
        height: 1fr;
        padding: 1 2;
    }
    #path-left VerticalScroll { width: 1fr; height: 1fr; }

    /* ── right pane ── */
    #lv-kicker { color: #7d90b8; height: 1; }
    #lv-title { color: #e9eef8; text-style: bold; height: 3; padding: 1 0 0 0; }
    #lv-module { color: #94a3bd; height: 1; }
    #lv-blurb { color: #cdd7ea; height: auto; padding: 1 0; }
    #lv-note { color: #7d90b8; height: auto; }
    #lv-action { height: auto; padding: 2 0 0 0; }
    #level-btn { margin: 2 0 0 0; }
    #level-btn.locked {
        background: #1a2438; color: #556180;
        border: solid #2c3a58;
        border-right: heavy #121a2e;
        border-bottom: heavy #121a2e;
    }
    /* playable: the locked fill, but the frame is lit */
    #level-btn.ready {
        background: #1a2438; color: #ffd166;
        border: solid #ffd166;
        border-right: heavy #8a6a12;
        border-bottom: heavy #8a6a12;
    }
    #level-btn.ready:hover { background: #22304a; }
    """

    class Selected(Message):
        """A level was picked in the list."""

        def __init__(self, level: Level) -> None:
            super().__init__()
            self.level = level

    def __init__(self, modules: list[Module], selected: Level, **kwargs) -> None:
        super().__init__(**kwargs)
        self.modules = modules
        self.selected = selected

    def on_module_card_picked(self, event: "ModuleCard.Picked") -> None:
        event.stop()
        self.select(event.level)

    def on_path_screen_selected(self, event: "PathScreen.Selected") -> None:
        event.stop()
        self.select(event.level)

    def select(self, level: Level) -> None:
        """Make `level` current: highlight its row and refresh the right pane."""
        self.selected = level
        self.app._selected = level
        self.app._refresh_header()
        for row in self.query(LevelRow):
            row.selected = row.level is level
            row.refresh()
        self._update_detail()
        self._sync_footer()

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="path-left"):
            last = len(self.modules) - 1
            for index, module in enumerate(self.modules):
                yield ModuleCard(
                    module, self.selected,
                    top=index > 0,
                    bottom=index < last,
                )
        with Vertical(id="path-right"):
            yield from self._detail()

    def _detail(self):
        level = self.selected
        module = next(
            (m for m in self.modules if level in m.levels), self.modules[0]
        )
        done = level.state == "done"
        locked = level.state == "locked"

        yield Static(f"MODULE {module.number}  ·  LEVEL {level.number}", id="lv-kicker")
        yield Static(level.title, id="lv-title")
        yield Static(module.title, id="lv-module")
        yield Static(level.note or module.blurb, id="lv-blurb")

        if locked:
            yield Static("Clear the level before this one to unlock it.", id="lv-note")
            yield PixelButton(f"{LEVEL_ICON['locked']} Locked",
                              id="level-btn", classes="locked")
        elif done:
            yield Static("Completed  ·  replay any time", id="lv-note")
            yield PixelButton(f"{LEVEL_ICON['done']} Replay",
                              id="level-btn", classes="ready")
        else:
            yield Static("Not finished yet", id="lv-note")
            yield PixelButton(f"{LEVEL_ICON['unlocked']} Play",
                              id="level-btn", classes="ready")

    def on_mount(self) -> None:
        self.app._selected = self.selected
        self._sync_footer()

    def _sync_footer(self) -> None:
        try:
            foot = self.app.query_one("#pf-left", Static)
        except Exception:
            return
        level = self.selected
        module = next(
            (m for m in self.modules if level in m.levels), self.modules[0]
        )
        foot.update(
            f"Module {module.number} · {module.title}    "
            f"Level {level.number} · {level.title}"
        )

    def on_module_card_toggled(self, event: ModuleCard.Toggled) -> None:
        """Opening one module closes the others, like an accordion."""
        target = event.module
        was_open = target.open
        for module in self.modules:
            module.open = False
        target.open = not was_open
        self.rebuild()

    def rebuild(self) -> None:
        """Re-render both panes: the list highlight and the detail card."""
        left = self.query_one("#path-left", VerticalScroll)
        left.remove_children()
        last = len(self.modules) - 1
        left.mount_all([
            ModuleCard(m, self.selected, top=i > 0, bottom=i < last)
            for i, m in enumerate(self.modules)
        ])
        left.scroll_to(y=0, animate=False)

        self._update_detail()
        self._sync_footer()

    def _update_detail(self) -> None:
        """Refresh the right pane in place (ids stay stable)."""
        level = self.selected
        module = next(
            (m for m in self.modules if level in m.levels), self.modules[0]
        )
        done = level.state == "done"
        locked = level.state == "locked"

        self.query_one("#lv-kicker", Static).update(
            f"MODULE {module.number}  ·  LEVEL {level.number}"
        )
        self.query_one("#lv-title", Static).update(level.title)
        self.query_one("#lv-module", Static).update(module.title)
        self.query_one("#lv-blurb", Static).update(
            level.note or f"A new step in {module.title}."
        )

        if locked:
            note = "Clear the level before this one to unlock it."
            label, cls = f"{LEVEL_ICON['locked']} Locked", "locked"
        elif done:
            note = "Completed  ·  replay any time"
            label, cls = f"{LEVEL_ICON['done']} Replay", "ready"
        else:
            note = "Not finished yet"
            label, cls = f"{LEVEL_ICON['unlocked']} Play", "ready"

        self.query_one("#lv-note", Static).update(note)
        button = self.query_one("#level-btn", PixelButton)
        button.label = label
        # border(2) + padding(4) + one spare column: measured, not guessed —
        # at len+7 the content box was exactly the label width and Textual
        # clipped the last character
        button.styles.width = len(label) + 8
        button.set_class(cls == "locked", "locked")
        button.set_class(cls == "ready", "ready")


class Sidebar(Vertical):
    """Slide-in list of every level, shaped exactly like the course path.

    It reuses ModuleCard, so the sidebar and the path screen share one
    accordion: same dots, same connectors, same open/close behaviour. Only the
    width and the chrome differ.
    """

    DEFAULT_CSS = """
    Sidebar {
        layer: sidebar;
        position: absolute;
        offset: 0 4;
        width: 44;
        height: 1fr;
        background: #0f1626;
        border-right: thick #243049;
        padding: 0 0 1 0;
    }
    #sb-bar { height: 3; background: #161d30; }
    #sb-head {
        width: 1fr;
        height: 3;
        padding: 0 2;
        content-align: left middle;
        background: #161d30;
        color: #cdd7ea;
        text-style: bold;
    }
    #sb-close {
        width: 4;
        height: 3;
        content-align: center middle;
        background: #161d30;
        color: #94a3bd;
    }
    #sb-close:hover { color: #ffffff; background: #243049; }
    #sb-bar-gap { width: 1; height: 3; background: #161d30; }

    #sb-scroll {
        width: 1fr;
        height: 1fr;
        layout: vertical;
        overflow: hidden hidden;
    }
    #sb-foot {
        height: 1;
        padding: 0 2;
        color: #7d90b8;
    }
    """

    def __init__(self, modules: list[Module], current: Level | None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.modules = modules
        self.current = current

    def compose(self) -> ComposeResult:
        with Horizontal(id="sb-bar"):
            yield Static("Modules", id="sb-head")
            yield Static("✕", id="sb-close")
            yield Static("", id="sb-bar-gap")
        with Vertical(id="sb-scroll"):
            last = len(self.modules) - 1
            for index, module in enumerate(self.modules):
                yield ModuleCard(
                    module, self.current,
                    top=index > 0,
                    bottom=index < last,
                )
        yield Static("esc  close", id="sb-foot")

    class Closed(Message):
        """The sidebar asked to be dismissed."""

    def on_click(self, event) -> None:
        widget = event.widget
        if widget is not None and widget.id == "sb-close":
            self.post_message(self.Closed())

    def on_module_card_picked(self, event: "ModuleCard.Picked") -> None:
        event.stop()
        self.app._selected = event.level
        self.post_message(Sidebar.Chosen(event.level))

    def on_module_card_toggled(self, event: ModuleCard.Toggled) -> None:
        """Same accordion rule as the path screen: one open module at a time."""
        event.stop()
        target = event.module
        was_open = target.open
        for module in self.modules:
            module.open = False
        target.open = not was_open
        self.rebuild()

    def on_level_row_picked(self, event: "LevelRow.Picked") -> None:
        event.stop()
        self.post_message(Sidebar.Chosen(event.level))

    class Chosen(Message):
        def __init__(self, level: Level) -> None:
            super().__init__()
            self.level = level

    def rebuild(self) -> None:
        holder = self.query_one("#sb-scroll", Vertical)
        for child in list(holder.children):
            child.remove()
        last = len(self.modules) - 1
        holder.mount_all([
            ModuleCard(m, self.current, top=i > 0, bottom=i < last)
            for i, m in enumerate(self.modules)
        ])


class MoreMenu(Vertical):
    """The ⋯ menu: copy / reset / load, floated just above its button."""

    DEFAULT_CSS = """
    MoreMenu {
        layer: sidebar;
        position: absolute;
        width: 18;
        height: auto;
        background: #0f1626;
        border: round #3a4a6e;
        padding: 0;
    }
    MoreMenu PixelButton {
        width: 100%;
        min-width: 0;
        margin: 0;
        padding: 0 1;
        border: none;
        background: transparent;
        color: #cdd7ea;
        content-align: left middle;
    }
    MoreMenu PixelButton:hover { background: #1c2740; color: #ffffff; }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.styles.width = 18
        self.styles.height = "auto"

    def compose(self) -> ComposeResult:
        yield PixelButton("Copy", id="mm-copy")
        yield PixelButton("Reset", id="mm-reset")
        yield PixelButton("Load…", id="mm-load")

    class Chosen(Message):
        def __init__(self, action: str) -> None:
            super().__init__()
            self.action = action

    def on_button_pressed(self, event: Button.Pressed) -> None:
        event.stop()
        mapping = {"mm-copy": "copy", "mm-reset": "reset", "mm-load": "load"}
        action = mapping.get(event.button.id or "")
        if action:
            self.post_message(self.Chosen(action))


class SettingsPage(Vertical):
    """A full page of options, not a floating panel.

    It replaces the lesson like the path screen does, so it gets the whole
    frame instead of a cramped corner, and the accent colour it changes is
    visible immediately in the header above it.
    """

    DEFAULT_CSS = """
    SettingsPage {
        width: 1fr;
        height: 1fr;
        padding: 1 3;
        background: #0a0f1e;
    }
    #set-title {
        height: 3;
        content-align: left middle;
        color: #e9eef8;
        text-style: bold;
    }
    #set-sub {
        height: auto;
        padding: 0 0 1 0;
        color: #7d90b8;
    }
    .set-row {
        height: 3;
        width: 1fr;
        padding: 0 2;
        background: #0f1626;
        border: round #243049;
        content-align: left middle;
        color: #cdd7ea;
    }
    .set-row:hover { background: #16233d; border: round #5b9bf5; }
    .set-row-group { height: 3; width: 1fr; }
    .set-chip {
        width: 1fr;
        height: 3;
        padding: 0 1;
        background: #0f1626;
        border: round #243049;
        content-align: left middle;
        color: #cdd7ea;
    }
    .set-group {
        height: 3;
        padding: 1 0 0 0;
        color: #7d90b8;
        text-style: bold;
    }
    #set-snip-hint {
        height: auto;
        padding: 0 0 1 0;
        color: #7d90b8;
    }
    #set-hint {
        height: auto;
        padding: 1 0 0 0;
        color: #7d90b8;
    }
    """

    ACCENTS = [
        ("Blue", "#5b9bf5"),
        ("Mint", "#7ee787"),
        ("Violet", "#b392f0"),
        ("Amber", "#ffd166"),
        ("Rose", "#ff7b8a"),
    ]

    def __init__(self, accent: str, animate: bool, density: float, **kwargs) -> None:
        super().__init__(**kwargs)
        self.accent = accent
        self.animate = animate
        self.density = density
        self._reset_armed = False

    def compose(self) -> ComposeResult:
        yield Static("Settings", id="set-title")
        yield Static("Changes apply immediately.", id="set-sub")

        yield Static("APPEARANCE", classes="set-group")
        yield Static(self._accent_text(), id="set-accent", classes="set-row")
        yield Static(self._anim_text(), id="set-anim", classes="set-row")

        yield Static("FEEDBACK", classes="set-group")
        yield Static(self._conf_text(), id="set-conf", classes="set-row")

        yield Static("PROGRESS", classes="set-group")
        yield Static("Reset progress          clear levels and hints",
                     id="set-reset", classes="set-row")

        yield Static("INTELLISENSE", classes="set-group")
        for label, text in (
            ("Names", "variables, functions and classes in your file"),
            ("Members", "type `items.` to list methods of that value"),
            ("Builtins", "print, range, len, sum and the rest of Python"),
            ("Keys", "Tab or Enter inserts, Esc closes, ctrl+space opens"),
        ):
            yield Static(f"{label:<10} {text}", classes="set-row")
        yield Static("Click a row to change it. Esc returns to the lesson.",
                     id="set-hint")

    # -- labels -----------------------------------------------------------

    def _accent_name(self) -> str:
        for name, value in self.ACCENTS:
            if value == self.accent:
                return name
        return "Custom"

    def _accent_text(self) -> str:
        return f"Accent colour          {self._accent_name()}  ({self.accent})"

    def _anim_text(self) -> str:
        state = "on" if self.animate else "off"
        return f"Menu animation         {state}"

    def _conf_text(self) -> str:
        name = {0.025: "light", 0.055: "normal", 0.11: "heavy"}.get(
            self.density, str(self.density)
        )
        return f"Confetti               {name}"

    # -- events -----------------------------------------------------------

    class Closed(Message):
        """Leave the settings page."""

    class Changed(Message):
        def __init__(self, accent: str, animate: bool, density: float) -> None:
            super().__init__()
            self.accent = accent
            self.animate = animate
            self.density = density

    class ResetRequested(Message):
        """The reset row was clicked (already confirmed twice)."""

    def on_click(self, event) -> None:
        widget = event.widget
        if widget is None:
            return
        if widget.id == "set-accent":
            values = [value for _name, value in self.ACCENTS]
            index = values.index(self.accent) if self.accent in values else -1
            self.accent = values[(index + 1) % len(values)]
            self.query_one("#set-accent", Static).update(self._accent_text())
        elif widget.id == "set-anim":
            self.animate = not self.animate
            self.query_one("#set-anim", Static).update(self._anim_text())
        elif widget.id == "set-conf":
            order = [0.025, 0.055, 0.11]
            index = order.index(self.density) if self.density in order else 1
            self.density = order[(index + 1) % len(order)]
            self.query_one("#set-conf", Static).update(self._conf_text())
        elif widget.id == "set-reset":
            # first click arms it, second click does it
            if not self._reset_armed:
                self._reset_armed = True
                self.query_one("#set-reset", Static).update(
                    "Reset progress          click again to confirm"
                )
                return
            self.post_message(self.ResetRequested())
            return
        else:
            return
        self.post_message(self.Changed(self.accent, self.animate, self.density))


class LoadDialog(Vertical):
    """Ask for a .py path, over the editor, without leaving the lesson."""

    DEFAULT_CSS = """
    LoadDialog {
        layer: sidebar;
        position: absolute;
        offset: 0 8;
        width: 52;
        height: auto;
        background: #0f1626;
        border: thick #5b9bf5;
        padding: 0 0 1 0;
    }
    #load-head {
        height: 3;
        padding: 0 2;
        content-align: left middle;
        background: #161d30;
        color: #cdd7ea;
        text-style: bold;
    }
    #load-body { height: auto; width: 1fr; padding: 1 2; }
    #load-label { height: 1; color: #7d90b8; }
    #load-input { height: 1; background: #0a0f1e; border: none; padding: 0 1; }
    #load-hint { height: auto; padding: 1 0 0 0; color: #7d90b8; }
    #load-actions { height: 3; width: 1fr; padding: 1 0 0 0; align: right middle; }
    #load-actions PixelButton { margin: 0 0 0 1; }
    """

    def __init__(self, start: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self.styles.width = 52
        self.styles.height = "auto"
        self._start = start

    def compose(self) -> ComposeResult:
        yield Static("Load file", id="load-head")
        with Vertical(id="load-body"):
            yield Static("Path to a .py file", id="load-label")
            yield Input(placeholder="~/hello.py", id="load-input")
            yield Static("Tab to the button, or press Enter to load.",
                         id="load-hint")
            with Horizontal(id="load-actions"):
                yield PixelButton("Cancel", id="load-cancel")
                yield PixelButton("Load", id="load-go", classes="ready")

    def on_mount(self) -> None:
        self._centre()
        self.query_one("#load-input", Input).focus()

    def _centre(self) -> None:
        """Put the dialog in the middle of the screen.

        `offset` is relative to the top-left corner, so centring means
        (screen - dialog) / 2 on both axes. The height is known only after
        layout, hence the call_after_refresh in the caller.
        """
        screen_w, screen_h = self.app.size
        outer = self.outer_size
        width = outer.width or 52
        height = outer.height or 15
        left = max(0, (screen_w - width) // 2)
        top = max(0, (screen_h - height) // 2)
        self.styles.offset = (left, top)

    class Closed(Message):
        """The dialog was dismissed."""

    class Loaded(Message):
        def __init__(self, path: str) -> None:
            super().__init__()
            self.path = path

    def _submit(self) -> None:
        self.post_message(self.Loaded(self.query_one("#load-input", Input).value.strip()))

    @on(Input.Submitted, "#load-input")
    def _submitted(self) -> None:
        self._submit()

    @on(Button.Pressed, "#load-cancel")
    def _cancel(self) -> None:
        self.post_message(self.Closed())

    @on(Button.Pressed, "#load-go")
    def _go(self) -> None:
        self._submit()


class ClickThroughScreen(Screen):
    """A screen where the confetti overlay never steals the mouse.

    Textual hit-tests the top-most widget, and the overlay spans the whole
    screen, so every click during the animation landed on the confetti
    instead of the buttons. Skipping the overlay keeps the app usable while
    it plays.
    """

    def get_widget_at(self, x: int, y: int):
        for widget, region in self.get_widgets_at(x, y):
            if not isinstance(widget, Confetti):
                return widget, region
        return super().get_widget_at(x, y)


# --------------------------------------------------------------------------- #
#  App
# --------------------------------------------------------------------------- #
class PyLearnApp(App):
    TITLE = "pylearn"

    modules: list[Module] = []
    """Filled in `on_load`; declared here so compose() can see it."""

    def on_load(self) -> None:
        self.modules = _build_modules()
        saved = load_progress()
        apply_progress(self.modules, saved)
        # restore the per-level wrong-answer counts that gate Hint/Solution
        for module in self.modules:
            for level in module.levels:
                slug = getattr(level.lesson, "slug", "")
                entry = saved.get("levels", {}).get(slug, {})
                if entry.get("failures"):
                    self.failures[slug] = int(entry["failures"])

    def persist(self) -> None:
        """Write the current state to disk. Cheap; called after each change."""
        save_progress(collect_progress(self))

    on_menu = True
    """The app opens on the menu; Start swaps it for the course path."""

    _selected: object = None
    """The Level currently chosen in the path/sidebar."""

    on_path = False
    """True while the module/level path is showing instead of the lesson."""
    ENABLE_COMMAND_PALETTE = False
    HORIZONTAL_BREAKPOINTS = [(0, "-narrow"), (90, "-wide")]

    #: Below this height the stacked layout has to give the editor priority.
    VERTICAL_BREAKPOINTS = [(0, "-short"), (30, "-tall")]

    BINDINGS = [
        Binding("ctrl+r,f5", "run_code", "Run", priority=True),
        Binding("ctrl+s", "submit_answer", "Submit", priority=True),
        Binding("ctrl+q", "quit", "Quit", priority=True),
        # path navigation — only meaningful while the path is showing
        Binding("up", "path_up", "Up", show=False),
        Binding("down", "path_down", "Down", show=False),
        Binding("enter", "path_enter", "Open", show=False),
        Binding("escape", "path_back", "Menu", show=False),
    ]

    def action_path_up(self) -> None:
        self._move_selection(-1)

    def action_path_down(self) -> None:
        self._move_selection(1)

    def action_path_enter(self) -> None:
        if not self.on_path:
            return
        path = self.query_one("#path", PathScreen)
        level = path.selected
        if level.state == "locked":
            self.notify("Clear the level above this one first.",
                        title="Locked", severity="warning", timeout=2)
            return
        self.show_lesson()

    def action_path_back(self) -> None:
        if self.load_open:
            self.close_load()
            return
        if self.more_open:
            self.close_more()
            return
        if self.settings_open:
            self.close_settings()
            return
        if self.sidebar_open:
            self.close_sidebar()
            return
        if not self.on_path:
            return
        for widget in self.query("#path"):
            widget.remove()
        self.on_path = False
        self._selected = None
        self.query_one("#path-wrap").remove_class("-on")
        self.query_one("#path-foot").remove_class("-on")
        self.query_one("#bottom").display = False
        self._refresh_header()
        self.on_menu = True
        self.query_one("#scene").display = True
        self._selected = None
        self._refresh_header()
        self.query_one("#start-btn", PixelButton).focus()

    def _move_selection(self, delta: int) -> None:
        """Walk the flat list of levels, opening the module as we go."""
        if not self.on_path:
            return
        path = self.query_one("#path", PathScreen)
        flat = [lv for m in self.modules for lv in m.levels]
        try:
            index = flat.index(path.selected)
        except ValueError:
            index = 0
        index = max(0, min(len(flat) - 1, index + delta))
        path.selected = flat[index]
        for module in self.modules:
            module.open = flat[index] in module.levels
        path.rebuild()

    CSS = f"""
    Screen {{ background: {BG}; color: {TEXT}; layers: base sidebar confetti; }}
    * {{ scrollbar-size-vertical: 1; scrollbar-color: {LINE}; scrollbar-color-hover: {BTN_EDGE};
         scrollbar-background: {BG}; scrollbar-background-hover: {BG}; scrollbar-corner-color: {BG}; }}

    /* Toasts default to the bottom-right corner, which is exactly where Back
       and Next live: for the three seconds a toast is up it swallowed the
       click. Move them up beside the top bar instead. */
    ToastRack {{ margin-bottom: 5; }}

    /* ───────── top bar ───────── */
    #topbar {{ height: 6; background: {BG}; border-bottom: solid {LINE}; padding: 1 1 0 1; }}
    /* the blank line above the bar is part of the padding, so the row of
       controls starts on line 2 and everything shares one baseline */
    #topbar > * {{ height: 3; content-align: left middle; }}
    #topbar > Label {{ height: 3; content-align: left middle; }}
    #coin {{ width: 2; color: #f2c94c; text-style: bold; }}
    #logo {{ width: auto; color: white; text-style: bold; margin-right: 2; }}
    #crumbs {{ width: auto; color: {MUTED}; margin-right: 2; }}
    #progressbar {{ width: 1fr; max-width: 28; min-width: 8; height: 3;
              padding: 1 0 1 0; content-align: left middle; }}
    #pct {{ width: auto; color: {MUTED}; margin-left: 1; }}
    #top-gap {{ width: 1fr; }}
    /* two quiet icon buttons, same shape as the sidebar toggle */
    .topact {{
        width: auto;
        height: 3;
        min-width: 5;
        padding: 0 1;
        margin: 0 0 0 1;
        background: #0f1626;
        color: #cdd7ea;
        text-style: bold;
        content-align: center middle;
        border: round #3a4a6e;
    }}
    .topact:hover {{ background: #1c2740; color: #ffffff; border: round #6f8ab8; }}
    .topact:focus {{ background: #1c2740; color: #ffffff; border: round {YELLOW}; }}

    /* ───────── body split ───────── */
    #body {{ height: 1fr; }}

    #lesson {{ width: 38%; min-width: 34; background: {BG}; border-right: thick {LINE};
               padding: 0 2 1 2; }}
    .prose {{ margin-top: 1; color: {TEXT}; }}
    .bullet {{ margin: 0 0 0 3; color: {TEXT}; }}
    #sprites {{ margin-top: 1; height: auto; }}

    .section-header {{ background: {PANEL}; color: {HEADTEXT}; text-style: bold; height: 3;
                       content-align: left middle; padding: 0 2; margin: 1 -2 0 -2; }}
    /* the first bar is a tab strip: no gap above it */
    .section-header:first-child {{ margin: 0 -2 0 -2; }}

    .code-block {{ height: auto; background: {CODEBG}; margin-top: 1; padding: 1 2; }}
    .cb-text {{ width: 1fr; height: auto; }}
    .cb-copy {{ width: 2; color: {MUTED}; }}
    .cb-copy:hover {{ color: white; }}

    .help-item {{ height: auto; margin-top: 1; background: {HELPBG}; }}
    .hi-head {{ height: 3; padding: 0 2; align: left middle; }}
    .hi-head:hover {{ background: #1c2740; }}
    .hi-icon {{ width: 4; color: {MUTED}; }}
    .hi-title {{ width: 1fr; text-style: bold; color: {TEXT}; }}
    .hi-chev {{ width: 2; color: {MUTED}; }}
    .hi-body {{ display: none; padding: 0 2 1 6; color: {MUTED}; }}
    .help-item.-open .hi-body {{ display: block; }}

    /* ───────── right: editor + terminal ───────── */
    #workspace {{ width: 1fr; background: {BG}; }}
    #tabs {{ height: 3; background: {PANEL}; }}
    #tab {{ width: auto; height: 3; padding: 1 3 0 2; color: white; text-style: bold; }}
    #editor-wrap {{ height: 2fr; background: {EDITOR}; }}

    #editor {{ height: 1fr; background: {EDITOR}; border: none; padding: 1 1 0 1; }}
    #editor:focus {{ border: none; background-tint: transparent; }}

    #actions {{ height: 5; background: {EDITOR}; padding: 0 2 1 2; align: right bottom; }}
    #actions-gap {{ width: 1fr; }}

    #term-head {{ height: 3; background: {PANEL}; color: {HEADTEXT}; text-style: bold;
                  padding: 1 2 0 2; }}
    #term-wrap {{ height: 1fr; background: {BG}; border: round #1e293b; }}
    #output {{ display: none; background: {BG}; padding: 1 2; height: 1fr; }}
    #placeholder {{ height: 1fr; align: center middle; }}
    #ph-icon {{ width: 100%; text-align: center; color: #6f80a0; text-style: bold; }}
    #ph-text {{ width: 100%; text-align: center; color: {MUTED}; margin-top: 1; }}
    #term-wrap.-ran #output {{ display: block; }}
    #term-wrap.-ran #placeholder {{ display: none; }}

    /* ───────── bottom bar ───────── */
    #bottom {{ height: 5; background: {BG}; border-top: solid {LINE}; padding: 0 2; align: left middle; }}
    #ex-info {{ width: auto; height: 3; margin-left: 2; }}
    #ex-title {{ text-style: bold; color: {TEXT}; height: 1; }}
    #ex-row {{ height: 1; width: auto; }}
    #ex-sub {{ color: {MUTED}; width: auto; }}
    #bottom-gap {{ width: 1fr; }}

    /* ───────── pixel buttons: square outline + hard bottom/right shadow ───────── */
    PixelButton {{
        height: 3; min-width: 10; width: auto; padding: 0 2; margin-left: 2;
        content-align: center middle;
        text-style: bold; color: {TEXT}; background: {BTN_DARK};
        border: solid {BTN_DARK_EDGE};
        border-right: heavy {BTN_DARK_SHADOW};
        border-bottom: heavy {BTN_DARK_SHADOW};
    }}
    PixelButton:hover {{ background: {BTN_DARK_HOVER}; }}
    PixelButton:focus {{ text-style: bold; background-tint: transparent; }}
    PixelButton.-active {{ background: {BTN_DARK_HOVER}; border-right: solid {BTN_DARK_EDGE};
                           border-bottom: solid {BTN_DARK_EDGE};
                           border-left: heavy {BTN_DARK_SHADOW}; border-top: heavy {BTN_DARK_SHADOW}; }}

    /* Submit: the Run button's dark fill, framed in blue instead of filled
       with it, so it reads as the primary action without shouting. */
    PixelButton.blue {{
        background: {BTN_DARK}; color: {TEXT};
        border: solid {BTN_EDGE};
        border-right: heavy {BTN_SHADOW};
        border-bottom: heavy {BTN_SHADOW};
    }}
    PixelButton.blue:hover {{ background: {BTN_DARK_HOVER}; color: #ffffff; }}
    PixelButton.blue.-active {{ background: #16233d; }}

    PixelButton.icon {{ min-width: 7; padding: 0 1; }}
    #menu-btn {{ margin-left: 0; }}
    #more-btn {{ margin-left: 0; }}

    /* ───────── main menu: scene behind a floating Start button ───────── */
    #scene {{ width: 1fr; height: 1fr; align: center middle; }}
    #path-wrap {{ display: none; height: 1fr; width: 1fr; }}
    #path-wrap.-on {{ display: block; }}
    #settings-wrap {{ display: none; height: 1fr; width: 1fr; }}
    #settings-wrap.-on {{ display: block; }}
    /* the title is painted in the scene; the button hangs just below it,
       which lands it in the middle of the frame */

    /* Menu button: a normal PixelButton whose fill matches the water behind
       it, so only the frame and label show. Textual has no alpha between
       widgets — this is as transparent as a widget can look. */
    PixelButton.ghost {{
        color: {YELLOW};
        border: solid {YELLOW};
        border-right: heavy #6b4f00;
        border-bottom: heavy #6b4f00;
        text-style: bold;
    }}
    PixelButton.ghost:hover {{ background: #2a7fbb; color: #fff3b0; border: solid #fff3b0; }}
    PixelButton.ghost.-active {{ background: #1c6ea6; }}
    PixelButton.ghost:focus {{ background-tint: transparent; }}

    /* the title is painted into the scene; this margin puts the button in the
       gap below it instead of on top of the wordmark */
    #start-btn {{ margin: 10 0 0 0; }}

    /* ───────── path footer ───────── */
    #path-foot {{
        display: none;
        height: 3;
        background: {BG};
        border-top: solid {LINE};
        padding: 0 2;
        align-vertical: middle;
    }}
    #path-foot.-on {{ display: block; }}
    #pf-left {{ width: auto; color: {MUTED}; }}
    #pf-gap {{ width: 1fr; }}
    #pf-keys {{ width: auto; color: {MUTED}; }}

    /* ───────── narrow (phone portrait): stack lesson over editor ───────── */
    Screen.-narrow #body {{ layout: vertical; }}
    Screen.-narrow #lesson {{ width: 100%; min-width: 0; height: 40%; border-right: none;
                              border-bottom: thick {LINE}; }}
    Screen.-narrow #workspace {{ width: 100%; height: 1fr; }}
    /* A short terminal cannot afford both panes stacked: the lesson keeps a
       sliver and the editor keeps enough rows to actually type in. */
    Screen.-short #lesson {{ height: 6; }}
    Screen.-short #editor-wrap {{ height: 1fr; min-height: 7; }}
    Screen.-short #term-wrap {{ height: 6; }}
    Screen.-short #bottom {{ height: 3; }}
    /* the button row is 5 rows tall normally; on a short terminal it costs
       the editor half its height, so squeeze it to one */
    Screen.-short #actions {{ height: 3; }}
    Screen.-short #actions PixelButton {{ min-width: 8; padding: 0 1; }}
    Screen.-narrow #crumbs {{ display: none; }}
    Screen.-narrow PixelButton {{ min-width: 8; padding: 0 1; margin-left: 1; }}
    """

    # ------------------------------------------------------------------ #
    def get_default_screen(self) -> Screen:
        """Use the click-through screen, so confetti never blocks the mouse."""
        return ClickThroughScreen(id="_default")

    def compose(self) -> ComposeResult:
        # top bar
        with Horizontal(id="topbar"):
            yield Label("●", id="coin")
            yield Label("pylearn", id="logo")
            yield Label(
                f"Python  /  [b {TEXT}]Hello World[/]", id="crumbs", markup=True
            )
            yield ProgressBar(id="progressbar")
            yield Label("0%", id="pct")
            yield Static("", id="top-gap")
            yield PixelButton("Home", id="home-btn", classes="topact")
            yield PixelButton("Setup", id="settings-btn", classes="topact")

        # ───── main menu ─────
        with Beach(id="scene"):
            yield PixelButton("Start", id="start-btn", classes="ghost")

        # ───── course path (built on demand) ─────
        yield Vertical(id="path-wrap")

        # ───── settings page (built on demand) ─────
        yield Vertical(id="settings-wrap")

        # ───── path footer ─────
        with Horizontal(id="path-foot"):
            yield Static("", id="pf-left")
            yield Static("", id="pf-gap")
            yield Static("↑ ↓  move     enter  open/play     esc  back to menu",
                         id="pf-keys")

        with Horizontal(id="body"):
            # ───── lesson ─────
            with VerticalScroll(id="lesson"):
                yield from self._lesson_flow()

            # ───── editor + terminal ─────
            with Vertical(id="workspace"):
                with Horizontal(id="tabs"):
                    yield Label("🐍  script.py", id="tab")
                with Vertical(id="editor-wrap"):
                    yield PyTextArea(
                        STARTER_CODE,
                        id="editor",
                        show_line_numbers=True,
                        tab_behavior="indent",
                    )
                    yield SignatureHint(id="signature")
                    with Horizontal(id="actions"):
                        yield PixelButton("⋯", id="more-btn", classes="icon")
                        yield Static("", id="actions-gap")
                        yield PixelButton("▶  Run", id="run-btn")
                        yield PixelButton("Submit answer", id="submit-btn", classes="blue")
                yield Static("Terminal", id="term-head")
                with Vertical(id="term-wrap"):
                    yield RichLog(id="output", markup=True, wrap=True, highlight=False)
                    with Vertical(id="placeholder"):
                        yield Label("‹ ›", id="ph-icon")
                        yield Label("Click [b]Run[/b] to view your results", id="ph-text", markup=True)

        # bottom bar
        with Horizontal(id="bottom"):
            yield PixelButton("≣", id="menu-btn", classes="icon")
            with Vertical(id="ex-info"):
                yield Label("Setting Up", id="ex-title")
                with Horizontal(id="ex-row"):
                    yield Label("Exercise 1 / 5", id="ex-sub")
            yield Static("", id="bottom-gap")
            yield PixelButton("Back", id="back-btn")
            yield PixelButton("Next", id="next-btn")

    # ------------------------------------------------------------------ #
    def on_mount(self) -> None:
        self._refresh_header()

        # the menu owns the screen until Start is pressed
        self.query_one("#body").display = False
        self.query_one("#bottom").display = False
        self.query_one("#start-btn", PixelButton).focus()

        editor = self.query_one("#editor", PyTextArea)
        editor.register_theme(
            TextAreaTheme(
                name="pylearn",
                base_style=Style(color=TEXT, bgcolor=EDITOR),
                gutter_style=Style(color=GUTTER, bgcolor=EDITOR),
                cursor_style=Style(color=EDITOR, bgcolor=TEXT),
                cursor_line_style=Style(bgcolor="#16233d"),
                cursor_line_gutter_style=Style(color="#a9c0e8", bgcolor="#16233d"),
                bracket_matching_style=Style(bgcolor="#1e3a6b"),
                selection_style=Style(bgcolor="#1e3a6b"),
                syntax_styles={
                    "comment": Style(color=COMMENT),
                    "string": Style(color=STRING),
                    "function.builtin": Style(color=ORANGE),
                    "function": Style(color=ORANGE),
                    "keyword": Style(color=KEYWORD),
                    "number": Style(color=NUMBER),
                },
            )
        )
        editor.theme = "pylearn"
        editor.cursor_blink = True
        # put the cursor on line 3 like the real lesson wants; focus stays on
        # the menu until Start is pressed
        editor.move_cursor((2, 0))
        self.query_one("#start-btn", PixelButton).focus()

    # ------------------------------------------------------------------ #
    def _load_level(self, level: "Level") -> None:
        """Swap the lesson content, editor starter and footer labels.

        The level is re-rolled first: every visit gets fresh random values, so
        the answer cannot be memorised from a previous attempt.
        """
        lesson = level.lesson
        if lesson is None:
            return
        lesson.roll()
        level.note = lesson.hint
        holder = self.query_one("#lesson", VerticalScroll)
        for child in list(holder.children):
            child.remove()
        holder.mount_all(list(self._lesson_flow()))
        editor = self.query_one("#editor", PyTextArea)
        editor.text = lesson.start
        editor.move_cursor((max(0, len(lesson.start.splitlines()) - 1), 0))
        editor.reindex()
        if editor._menu is not None:
            editor._menu.hide()
        try:
            self.query_one("#signature", SignatureHint).hide()
        except Exception:
            pass
        self.query_one("#ex-title", Label).update(
            f"{self._module_of(level).title}"
        )
        module = self._module_of(level)
        self.query_one("#ex-sub", Label).update(
            f"Exercise {level.exercise} · {level.number}/{len(module.levels)}"
        )
        self._last_stdout = ""

    def _module_of(self, level: "Level") -> "Module":
        for module in self.modules:
            if level in module.levels:
                return module
        return self.modules[0]

    def _lesson_flow(self):
        """Build the left column from the selected level's content.

        Everything here comes from `lessons/*.md`; nothing is hardcoded, so
        adding a level file is enough to make it appear.
        """
        lesson = self.current_lesson()
        if lesson is None:
            yield Static("No lesson loaded.", classes="prose")
            return

        yield Static("Learn", classes="section-header")
        yield from self._render_blocks(lesson.learn)
        yield Static("Instructions", classes="section-header")
        yield from self._render_blocks(lesson.instructions)
        yield Static("Help", classes="section-header")
        failures = self._failures_for(lesson)
        if lesson.hint:
            yield HelpItem("♡", "Hint", lesson.hint,
                           locked=failures < HINT_AFTER,
                           unlock_at=HINT_AFTER, failures=failures)
        if lesson.solution:
            yield HelpItem("◉", "Solution", lesson.solution,
                           locked=failures < SOLUTION_AFTER,
                           unlock_at=SOLUTION_AFTER, failures=failures)

    def _failures_for(self, lesson) -> int:
        """How many times this level has been submitted wrong."""
        return self.failures.get(getattr(lesson, "slug", ""), 0)

    def _bump_failures(self, lesson) -> int:
        slug = getattr(lesson, "slug", "")
        self.failures[slug] = self.failures.get(slug, 0) + 1
        return self.failures[slug]

    def _refresh_help(self) -> None:
        """Push the new failure count into the locked help rows."""
        lesson = self._selected.lesson if self._selected else None
        if lesson is None:
            return
        count = self._failures_for(lesson)
        for item in self.query(HelpItem):
            item.unlock(count)

    def _render_blocks(self, blocks):
        for block in blocks:
            if block.kind == "code":
                yield CodeBlock(self._highlight(block.text), block.text)
            elif block.kind == "out":
                yield CodeBlock(block.text, block.text)
            elif block.kind == "sprites":
                names = [n.strip() for n in block.text.split(",") if n.strip()]
                art = [SPRITES[n] for n in names if n in SPRITES]
                if art:
                    yield Static(sprite_row(art), classes="sprites")
            elif block.kind == "li":
                yield Static(f"•  {block.text}", classes="bullet")
            else:
                yield Static(self._markup(block.text), classes="prose")

    def _markup(self, text: str) -> str:
        """Markdown-ish inline formatting -> Textual console markup.

        Inline code is pulled out first and parked behind a placeholder: a
        backticked `*` or `_` must never be read as emphasis. Everything else
        is then free to run over the remaining text, and the code spans are
        put back at the end already escaped.
        """
        spans: list[str] = []

        def park(match: re.Match) -> str:
            spans.append(match.group(1))
            return f"\x00{len(spans) - 1}\x00"

        text = re.sub(r"`([^`]+)`", park, text)
        text = re.sub(r"\*\*(.+?)\*\*", r"[b]\1[/b]", text)
        text = re.sub(r"(?<!\w)\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"[i]\1[/i]", text)
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"[u]\1[/u]", text)

        def restore(match: re.Match) -> str:
            code = spans[int(match.group(1))]
            # escape so a bracket inside the snippet cannot open a tag
            code = code.replace("[", "\\[")
            return f"[#8fc3ff on #16233d] {code} [/]"

        return re.sub(r"\x00(\d+)\x00", restore, text)

    def _highlight(self, code: str) -> str:
        """Colour a code snippet with the same lexer as the editor."""
        out = []
        for _index, ttype, value in PythonLexer(stripnl=False).get_tokens_unprocessed(code):
            escaped = value.replace("[", "\\[")
            if ttype in Token.Comment:
                out.append(f"[{COMMENT}]{escaped}[/]")
            elif ttype in Token.Literal.String:
                out.append(f"[{STRING}]{escaped}[/]")
            elif ttype in Token.Keyword:
                out.append(f"[{KEYWORD}]{escaped}[/]")
            elif ttype in Token.Literal.Number:
                out.append(f"[{NUMBER}]{escaped}[/]")
            elif ttype in Token.Name.Builtin or ttype in Token.Name.Function:
                out.append(f"[{ORANGE}]{escaped}[/]")
            else:
                out.append(escaped)
        return "".join(out)

    def current_lesson(self):
        """The lessons.Level behind the current selection."""
        for module in self.modules:
            for level in module.levels:
                if level.lesson is not None and getattr(self, "_selected", None) is level:
                    return level.lesson
        for module in self.modules:
            for level in module.levels:
                if level.lesson is not None:
                    return level.lesson
        return None

    # ------------------------------------------------------------------ #
    async def action_run_code(self) -> None:
        code = self.query_one("#editor", TextArea).text
        wrap = self.query_one("#term-wrap")
        log = self.query_one("#output", RichLog)
        wrap.add_class("-ran")
        log.clear()
        log.write(f"[{MUTED}]$ python script.py[/]")
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-c", code,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            try:
                out, err = await asyncio.wait_for(proc.communicate(), timeout=5)
            except asyncio.TimeoutError:
                proc.kill()
                log.write(f"[{ERROR}]Timed out after 5 seconds.[/]")
                return
        except Exception as exc:  # noqa: BLE001
            log.write(f"[{ERROR}]{exc}[/]")
            return
        self._last_stdout = out.decode(errors="replace")
        self._last_run_code = code
        for line in self._last_stdout.splitlines():
            log.write(Text(line, style=TEXT))
        for line in err.decode(errors="replace").splitlines():
            log.write(Text(line, style=ERROR))

    _last_stdout = ""
    _last_run_code: "str | None" = None

    async def _run_code(self, code: str) -> tuple[str, str, int]:
        """Run `code` in a subprocess; return (stdout, stderr, returncode)."""
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", code,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        try:
            out, err = await asyncio.wait_for(proc.communicate(), timeout=5)
        except asyncio.TimeoutError:
            proc.kill()
            return "", "Timed out after 5 seconds.", -1
        return (out.decode(errors="replace"),
                err.decode(errors="replace"),
                proc.returncode or 0)

    async def check_answer(self, level, lesson, code: str) -> tuple[bool, str]:
        """Decide whether `code` solves `lesson`.

        Compares stdout with the level's `expect`. In `strict` mode a program
        that exits non-zero is rejected even when it printed the right line,
        so a crash cannot pass as an answer.
        """
        mode = getattr(lesson, "check", "output")
        expect = (lesson.expect or "").strip()

        out, err, code_rc = await self._run_code(code)
        actual = out.strip()

        if expect and actual != expect:
            return False, describe_mismatch(expect, actual)
        if not expect and not actual:
            return False, "Run it first — nothing was printed."

        if mode == "strict" and code_rc != 0:
            first = err.strip().splitlines()[0] if err.strip() else "exit code"
            return False, f"The program failed: {first}"
        return True, ""

    def action_submit_answer(self) -> None:
        """Judge the answer, then react to it.

        Confetti is a reward, so it only fires on a correct answer. A wrong
        one gets a red line in the Terminal instead — no particle effect,
        because a wrong answer should not look like a celebration.
        """
        level = self._selected
        lesson = level.lesson if level is not None else None

        if not self.query_one("#editor", PyTextArea).text.strip():
            self.notify("Write some code first, then Run and submit.",
                        title="Editor is empty", severity="warning", timeout=4)
        elif lesson is None:
            self.notify("No lesson loaded.", severity="warning", timeout=3)
        else:
            self.run_worker(self._judge(level, lesson), exclusive=True)

    async def _judge(self, level, lesson) -> None:
        """Run the level's check, then react to the verdict."""
        editor = self.query_one("#editor", PyTextArea)
        code = editor.text

        # The answer must be the code that was actually run. Without this,
        # running the solution and then editing it still passed.
        if self._last_run_code is not None and code != self._last_run_code:
            self.notify("Press Run again — the code changed since it last ran.",
                        title="Run it first", severity="warning", timeout=4)
            return

        self.query_one("#term-wrap").add_class("-ran")
        ok, message = await self.check_answer(level, lesson, code)
        if ok:
            self._complete_level(level, lesson)
            return
        self._bump_failures(lesson)
        self._show_wrong(lesson.expect or "", self._last_stdout.strip(), message)
        self._refresh_help()
        self.persist()

    def _show_wrong(self, expected: str, actual: str, hint: str) -> None:
        """Report a wrong answer where the evidence is, and once in the corner.

        The red line stays in the Terminal so it can be re-read, which the
        toast cannot do; the toast is the glance-level signal. No particle
        effect: a wrong answer should not look like a celebration.
        """
        log = self.query_one("#output", RichLog)
        wrap = self.query_one("#term-wrap")
        wrap.add_class("-ran")
        log.write(Text(f"✗ {hint}", style=ERROR))
        self.notify(hint, title="✗ not quite", severity="warning", timeout=4)
        self._flash_terminal()

    def _flash_terminal(self) -> None:
        """Flash the Terminal border red once, then restore it."""
        wrap = self.query_one("#term-wrap")
        wrap.styles.border = ("round", ERROR)
        self.set_timer(0.55, lambda: setattr(
            wrap.styles, "border", ("round", "#1e293b")
        ))

    def _course_pct(self) -> int:
        """Percentage of the whole course that is finished."""
        flat = [lv for m in self.modules for lv in m.levels]
        if not flat:
            return 0
        done = sum(1 for lv in flat if lv.state == "done")
        return round(done * 100 / len(flat))

    def _refresh_header(self) -> None:
        """Keep the breadcrumb and the progress bar in agreement.

        Both are derived from the same place, so the picker and the lesson can
        never show two different numbers.
        """
        if self._selected is not None:
            module = self._module_of(self._selected)
            tail = (
                f"Python  /  {module.title}  /  "
                f"[b {TEXT}]{self._selected.title}[/]"
            )
        else:
            tail = f"Python  /  [b {TEXT}]Level select[/]"
        try:
            self.query_one("#crumbs", Label).update(tail)
        except Exception:
            pass

        pct = self._course_pct()
        try:
            self.query_one(ProgressBar).set_pct(pct)
            self.query_one("#pct", Label).update(f"{pct}%")
        except Exception:
            pass

    def _complete_level(self, level: "Level", lesson) -> None:
        """Mark the level done and move the progress bar."""
        # one burst, no banner — the toast already says what happened
        celebrate(self.screen, None, shots=1, density=self.confetti_density)
        level.state = "done"
        unlock_next(self.modules, level)
        self._refresh_header()
        self.notify("Correct!", title="Level complete", timeout=3)
        self.persist()

    sidebar_open = False
    settings_open = False
    more_open = False
    load_open = False
    confetti_density = 0.055
    accent = "#5b9bf5"
    failures: dict = {}
    """Wrong submissions per level slug, for gating the help rows."""

    # -- ⋯ menu -----------------------------------------------------------

    def toggle_more(self) -> None:
        if self.more_open:
            self.close_more()
        else:
            self.open_more()

    def open_more(self) -> None:
        if self.more_open:
            return
        self.more_open = True
        button = self.query_one("#more-btn", PixelButton)
        region = button.region
        menu = MoreMenu(id="more-menu")
        self.screen.mount(menu)
        # sit just above the button, right-aligned with it
        menu.styles.offset = (max(0, region.x - 5), max(0, region.y - 3))

    def close_more(self) -> None:
        if not self.more_open:
            return
        self.more_open = False
        for widget in self.query("#more-menu"):
            widget.remove()

    def on_click(self, event) -> None:
        """Clicking outside an open popup closes it.

        A click inside the popup must leave it open, so the popup's own
        region is checked before dismissing.
        """
        if not self.more_open:
            return
        menus = list(self.query("#more-menu"))
        if not menus:
            return
        region = menus[0].region
        if not (region.x <= event.screen_x < region.x + region.width
                and region.y <= event.screen_y < region.y + region.height):
            self.close_more()

    def on_more_menu_chosen(self, event: "MoreMenu.Chosen") -> None:
        event.stop()
        self.close_more()
        if event.action == "copy":
            self._copy_editor()
        elif event.action == "reset":
            self._reset_editor()
        elif event.action == "load":
            self.open_load()

    # -- editor actions ----------------------------------------------------

    def _copy_editor(self) -> None:
        text = self.query_one("#editor", PyTextArea).text
        self.copy_to_clipboard(text)
        self.notify("Editor contents copied.", timeout=2)

    def _reset_editor(self) -> None:
        lesson = self._selected.lesson if self._selected else None
        starter = lesson.start if lesson else STARTER_CODE
        self.query_one("#editor", PyTextArea).text = starter
        self.query_one("#editor", PyTextArea).move_cursor((0, 0))
        self.notify("Editor reset to the starter code.", timeout=2)

    def open_load(self) -> None:
        if self.load_open:
            return
        self.load_open = True
        dialog = LoadDialog(id="load-dialog")
        self.screen.mount(dialog)
        # re-centre once the dialog has been laid out and knows its height
        self.call_after_refresh(dialog._centre)

    def close_load(self) -> None:
        if not self.load_open:
            return
        self.load_open = False
        for widget in self.query("#load-dialog"):
            widget.remove()
        try:
            self.query_one("#editor", PyTextArea).focus()
        except Exception:
            pass

    def on_load_dialog_closed(self, event: "LoadDialog.Closed") -> None:
        event.stop()
        self.close_load()

    def on_load_dialog_loaded(self, event: "LoadDialog.Loaded") -> None:
        event.stop()
        path = event.path
        if not path:
            self.notify("No path given.", severity="warning", timeout=2)
            return
        target = Path(path).expanduser()
        if target.suffix != ".py":
            self.notify("That is not a .py file.", title="Load failed",
                        severity="warning", timeout=3)
            return
        try:
            source = target.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.notify(f"No such file: {target}", title="Load failed",
                        severity="error", timeout=3)
            return
        except OSError as exc:
            self.notify(str(exc), title="Load failed",
                        severity="error", timeout=3)
            return
        self.query_one("#editor", PyTextArea).text = source
        self.close_load()
        self.notify(f"Loaded {target.name}", timeout=2)

    # -- settings page -----------------------------------------------------

    def toggle_settings(self) -> None:
        if self.settings_open:
            self.close_settings()
        else:
            self.open_settings()

    def open_settings(self) -> None:
        """Show settings as a page, replacing whatever pane was visible."""
        if self.settings_open:
            return
        self.settings_open = True
        # remember where we came from so Esc can go back
        self._settings_from = (
            "path" if self.on_path else ("menu" if self.on_menu else "lesson")
        )
        self.query_one("#body").display = False
        self.query_one("#bottom").display = False
        self.query_one("#scene").display = False
        self.query_one("#path-wrap").remove_class("-on")
        self.query_one("#path-foot").remove_class("-on")
        scene = self.query_one("#scene", Beach)
        self.query_one("#settings-wrap").add_class("-on")
        holder = self.query_one("#settings-wrap")
        for child in list(holder.children):
            child.remove()
        holder.mount(
            SettingsPage(
                self.accent, scene.FPS > 0, self.confetti_density, id="settings"
            )
        )

    def close_settings(self) -> None:
        if not self.settings_open:
            return
        self.settings_open = False
        self.query_one("#settings-wrap").remove_class("-on")
        for widget in self.query("#settings"):
            widget.remove()
        where = getattr(self, "_settings_from", "lesson")
        if where == "menu":
            self.on_menu = True
            self.query_one("#scene").display = True
        elif where == "path":
            self.show_path()
        else:
            self.on_path = False
            self.query_one("#body").display = True
            self.query_one("#bottom").display = True
            try:
                self.query_one("#editor", PyTextArea).focus()
            except Exception:
                pass

    def on_settings_page_reset_requested(
        self, event: "SettingsPage.ResetRequested"
    ) -> None:
        event.stop()
        self.reset_progress()

    def reset_progress(self) -> None:
        """Wipe the save file and put the course back to its starting state."""
        try:
            PROGRESS_FILE.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            self.notify(f"Could not delete the save file: {exc}",
                        title="Reset failed", severity="error", timeout=4)
            return
        self.failures.clear()
        for module in self.modules:
            module.levels[0].state = "unlocked"
            for index, level in enumerate(module.levels):
                level.state = "unlocked" if index == 0 else "locked"
        self.persist()
        self._refresh_header()
        self.notify("Progress cleared.", title="Reset", timeout=2)
        self.close_settings()

    def on_settings_page_changed(self, event: "SettingsPage.Changed") -> None:
        event.stop()
        scene = self.query_one("#scene", Beach)
        scene.set_animated(event.animate)
        self.confetti_density = event.density
        if event.accent != self.accent:
            self.accent = event.accent
            self.apply_accent(event.accent)

    def apply_accent(self, colour: str) -> None:
        """Repaint everything that carries the accent colour.

        Textual cannot re-evaluate CSS variables at runtime, so the few
        widgets that matter are restyled directly. That is enough for the
        change to be visible in the header, which is where the user is
        looking while they click.
        """
        try:
            self.query_one("#logo", Label).styles.color = colour
        except Exception:
            pass
        try:
            self.query_one("#coin", Label).styles.color = colour
        except Exception:
            pass
        for selector in ("#home-btn", "#settings-btn"):
            try:
                self.query_one(selector, PixelButton).styles.border = (
                    "round", colour
                )
            except Exception:
                pass
        try:
            bar = self.query_one(ProgressBar)
            bar.accent = colour
            bar.refresh()
        except Exception:
            pass
        try:
            self.query_one("#ex-title", Label).styles.color = colour
        except Exception:
            pass

    def go_home(self) -> None:
        """Go up one screen: lesson -> level picker -> beach menu.

        It used to jump two levels at once from the lesson, so pressing Home
        inside a level dropped you straight onto the splash screen and the
        picker was never reachable except through Esc.
        """
        if self.settings_open:
            self.close_settings()
        if self.sidebar_open:
            self.close_sidebar()

        if not self.on_menu and not self.on_path:
            # in the lesson -> back to the level picker
            self.query_one("#body").display = False
            self.query_one("#bottom").display = False
            self.show_path()
            return

        if self.on_path:
            # on the picker -> back to the beach menu
            for widget in self.query("#path"):
                widget.remove()
            self.on_path = False
            self.query_one("#path-wrap").remove_class("-on")
            self.query_one("#path-foot").remove_class("-on")
            self.query_one("#body").display = False
            self.query_one("#bottom").display = False
            self.on_menu = True
            self.query_one("#scene").display = True
            self._selected = None
            self._refresh_header()
            self.query_one("#start-btn", PixelButton).focus()

    def toggle_sidebar(self) -> None:
        """Open or close the level list from the footer's ≣ button."""
        if self.on_menu:
            return          # nothing to list until the lesson exists
        if self.sidebar_open:
            self.close_sidebar()
        else:
            self.open_sidebar()

    def open_sidebar(self) -> None:
        if self.sidebar_open:
            return
        self.sidebar_open = True
        current = self._current_level()
        # open the module that holds the current level, like the path does
        for module in self.modules:
            module.open = current in module.levels
        self.screen.mount(Sidebar(self.modules, current, id="sidebar"))

    def close_sidebar(self) -> None:
        if not self.sidebar_open:
            return
        self.sidebar_open = False
        for widget in self.query("#sidebar"):
            widget.remove()
        try:
            self.query_one("#editor", PyTextArea).focus()
        except Exception:
            pass

    def _current_level(self) -> Level | None:
        """The level the path last had selected, if any."""
        try:
            return self.query_one("#path", PathScreen).selected
        except Exception:
            return next(
                (lv for m in self.modules for lv in m.levels
                 if lv.state == "unlocked"),
                None,
            )

    def on_sidebar_closed(self, event: "Sidebar.Closed") -> None:
        event.stop()
        self.close_sidebar()

    def on_sidebar_chosen(self, event: "Sidebar.Chosen") -> None:
        event.stop()
        level = event.level
        if level.state == "locked":
            self.notify("Clear the level above this one first.",
                        title="Locked", severity="warning", timeout=2)
            return
        self.close_sidebar()
        # actually switch the lesson, not just close the panel
        self._selected = level
        self._load_level(level)
        self.notify(
            f"Exercise {level.exercise} · {level.title}", timeout=2
        )

    @on(Button.Pressed, "#start-btn")
    def _start_pressed(self) -> None:
        self.start_lesson()

    def start_lesson(self) -> None:
        """Leave the menu and show the course path."""
        if not self.on_menu:
            return
        self.on_menu = False
        self.query_one("#scene").display = False
        self.query_one("#bottom").display = True
        self.show_path()

    def show_path(self) -> None:
        """Swap the lesson out for the module/level path."""
        self.on_path = True
        self.query_one("#body").display = False
        self.query_one("#bottom").display = False
        self.query_one("#path-wrap").add_class("-on")
        self.query_one("#path-foot").add_class("-on")
        if not self.query_one("#path-wrap").children:
            flat = [lv for m in self.modules for lv in m.levels]
            selected = (
                next((lv for lv in flat if lv.state == "unlocked"), None)
                or next((lv for lv in flat if lv.state != "done"), None)
                or (flat[0] if flat else None)
            )
            if selected is None:
                return
            for module in self.modules:
                module.open = selected in module.levels
            self.query_one("#path-wrap").mount(
                PathScreen(self.modules, selected, id="path")
            )
        self._refresh_header()

    def show_lesson(self) -> None:
        """Enter the editor for the selected level."""
        if self._selected is not None:
            self._load_level(self._selected)
        self.on_path = False
        for widget in self.query("#path"):
            widget.remove()
        self.query_one("#path-wrap").remove_class("-on")
        self.query_one("#path-foot").remove_class("-on")
        self.query_one("#bottom").display = True
        self.query_one("#body").display = True
        self._refresh_header()
        editor = self.query_one("#editor", PyTextArea)
        editor.focus()
        editor.move_cursor((2, 0))

    def _flat_levels(self) -> list["Level"]:
        """Every level in course order, module by module."""
        return [lv for module in self.modules for lv in module.levels]

    def step_level(self, delta: int) -> None:
        """Move `delta` levels forward or back through the course.

        Back and Next used to drive a leftover per-module exercise counter
        that nothing else read, so they changed a label and nothing else.
        They now walk the course itself.
        """
        if self._selected is None:
            return
        flat = self._flat_levels()
        index = next(
            (i for i, lv in enumerate(flat) if lv is self._selected), None
        )
        if index is None:
            return
        target = index + delta
        if target < 0:
            # nothing before the first level: the list is the sensible place
            self.notify("First level — back to the level list.", timeout=2)
            self.show_path()
            return
        if target >= len(flat):
            self.notify("Last level of the course.", title="Done", timeout=2)
            return
        nxt = flat[target]
        if nxt.state == "locked":
            self.notify(
                "Finish this level to unlock the next one.",
                title="Locked", severity="warning", timeout=3,
            )
            return
        self._selected = nxt
        self._load_level(nxt)
        self._refresh_header()
        # a fresh level means a fresh terminal
        self.query_one("#term-wrap").remove_class("-ran")
        self.query_one("#output", RichLog).clear()
        self.query_one("#editor", PyTextArea).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "run-btn":
                self.run_worker(self.action_run_code(), exclusive=True)
            case "submit-btn":
                self.action_submit_answer()
            case "next-btn":
                self.step_level(1)
            case "level-btn":
                self.show_lesson()
            case "back-btn":
                self.step_level(-1)
            case "more-btn":
                self.toggle_more()
            case "menu-btn":
                self.toggle_sidebar()
            case "home-btn":
                self.go_home()
            case "settings-btn":
                self.toggle_settings()


if __name__ == "__main__":
    PyLearnApp().run()
