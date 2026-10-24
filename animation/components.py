"""Переиспользуемые элементы сцен: текст, панели кода, карточки структур ядра,
ячейки, таблица страниц, значки оборудования, стрелки и «капсулы» вызовов."""
import re

import numpy as np
from manim import *

from style import *

STRUT = "█"  # полный блок: одинаковые высота и базовая линия у всех строк


# ---------------------------------------------------------------- текст ---

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def span(s: str, color: str) -> str:
    return f'<span foreground="{color}">{esc(s)}</span>'


def txt(s, size=22, color=TEXT, weight=NORMAL, font=SANS):
    return Text(s, font=font, font_size=size, color=color, weight=weight)


def mono(s, size=20, color=TEXT, weight=NORMAL):
    return Text(s, font=MONO, font_size=size, color=color, weight=weight)


def rich(s, size=24, color=TEXT, accent=YELLOW, font=SANS):
    """Текст с разметкой: *акцент* выделяется цветом, `код` — моноширинным шрифтом."""
    out = []
    for part in re.split(r"(\*[^*]+\*|`[^`]+`)", s):
        if len(part) > 1 and part[0] == part[-1] == "*":
            out.append(span(part[1:-1], accent))
        elif len(part) > 1 and part[0] == part[-1] == "`":
            out.append(f'<span font_family="{MONO}" foreground="{SYNTAX["fn"]}">'
                       f"{esc(part[1:-1])}</span>")
        else:
            out.append(esc(part))
    return MarkupText("".join(out), font=font, font_size=size, color=color)


C_KEYWORDS = {"int", "char", "void", "unsigned", "uint32_t", "size_t", "ssize_t",
              "off_t", "struct", "const", "for", "while", "if", "else", "return"}
_C_TOKEN = re.compile(r"(?P<com>//.*)|(?P<str>\"[^\"]*\"|'[^']*')"
                      r"|(?P<num>\b0x[0-9A-Fa-f]+\b|\b\d+\b)|(?P<id>[A-Za-z_]\w*)"
                      r"|(?P<ws>\s+)|(?P<op>.)")


def c_markup(src: str) -> str:
    """Подсветка одной строки на C в разметку Pango."""
    out = []
    for m in _C_TOKEN.finditer(src):
        kind, s = m.lastgroup, m.group()
        if kind == "ws":
            out.append(s)
            continue
        if kind == "id":
            if s in C_KEYWORDS:
                kind = "kw"
            elif s == "NULL" or (s.isupper() and len(s) > 1):
                kind = "const"
            elif src[m.end():].lstrip().startswith("("):
                kind = "fn"
            else:
                kind = "text"
        elif kind == "op":
            kind = "punct" if s in "=*&|+-<>" else "text"
        out.append(span(s, SYNTAX[kind]))
    return "".join(out)


class CodeLine(VGroup):
    """Строка моноширинного текста. Невидимые «распорки» по краям задают общую высоту
    и базовую линию, поэтому строки ровно выстраиваются и центрируются."""

    def __init__(self, markup: str, size: float = 20):
        text = MarkupText(STRUT + markup + STRUT, font=MONO, font_size=size)
        left, right = text[0], text[-1]
        text.remove(left, right)
        struts = VGroup(left, right).set_opacity(0)
        super().__init__(struts, text)
        self.text = text


def code_line(src, size=20):
    """`src` — строка на C (подсветится сама) или список пар (текст, цвет)."""
    if isinstance(src, str):
        return CodeLine(c_markup(src), size)
    return CodeLine("".join(span(t, c) for t, c in src), size)


def sub_glyphs(line, src, sub):
    """Глифы подстроки `sub` в строке `line`, набранной из текста `src`
    (пробелы в Text не становятся глифами, поэтому считаем только непробельные)."""
    i0 = len(src[:src.index(sub)].replace(" ", ""))
    return line.text[i0:i0 + len(sub.replace(" ", ""))]


# ------------------------------------------------------------ контейнеры ---

def tint(color, k=0.16):
    """Непрозрачная заливка: цвет панели с примесью акцента."""
    return interpolate_color(ManimColor(PANEL), ManimColor(color), k)


def rbox(w, h, stroke=PANEL_EDGE, fill=PANEL, r=0.14, sw=2.0):
    box = RoundedRectangle(corner_radius=min(r, h / 2, w / 2), width=w, height=h)
    return box.set_fill(fill, 1).set_stroke(stroke, sw)


def tbox(w, h, color, r=0.14, sw=2.2, k=0.16):
    return rbox(w, h, color, tint(color, k), r, sw)


class CodePanel(VGroup):
    """Окно редактора с «кнопками» в заголовке и подсвеченным кодом на C."""

    def __init__(self, lines, title="main.c", size=20, width=None, pad=0.26, gap=0.07):
        self.fs = size
        self.lines = VGroup(*[code_line(s, size) for s in lines]).arrange(DOWN, buff=gap, aligned_edge=LEFT)
        head_h = 0.4
        w = width or self.lines.width + 2 * pad
        self.frame = rbox(w, self.lines.height + 2 * pad + head_h, PANEL_EDGE, PANEL, r=0.16)
        dots = VGroup(*[Dot(radius=0.05, color=c) for c in (RED, YELLOW, GREEN)]).arrange(RIGHT, buff=0.09)
        dots.move_to(self.frame.get_corner(UL) + np.array([0.2 + dots.width / 2, -head_h / 2, 0]))
        name = txt(title, 15, MUTED).next_to(dots, RIGHT, buff=0.2)
        y = self.frame.get_top()[1] - head_h
        sep = Line([self.frame.get_left()[0], y, 0], [self.frame.get_right()[0], y, 0]).set_stroke(PANEL_EDGE, 1.5)
        self.header = VGroup(dots, name, sep)
        self.lines.next_to(sep, DOWN, buff=pad).align_to(self.frame, LEFT).shift(RIGHT * (pad - 0.1))
        self.lines.set_z_index(2)
        super().__init__(self.frame, self.header, self.lines)

    def highlight(self, first, last=None, color=YELLOW):
        """Плашка за строками first..last (рисуется под текстом)."""
        last = first if last is None else last
        top = self.lines[first].get_top()[1] + 0.03
        bottom = self.lines[last].get_bottom()[1] - 0.03
        bar = RoundedRectangle(corner_radius=0.06, width=self.frame.width - 0.14, height=top - bottom)
        bar.set_fill(color, 0.14).set_stroke(color, 1.2, opacity=0.55)
        return bar.move_to([self.frame.get_x(), (top + bottom) / 2, 0]).set_z_index(1)

    def note(self, i, s, color=SYNTAX["com"]):
        """Комментарий справа от строки i (на той же базовой линии)."""
        n = code_line([(s, color)], self.fs).next_to(self.lines[i], RIGHT, buff=0.1)
        return n.set_z_index(2)


class Card(VGroup):
    """Карточка структуры ядра: заголовок и строки-поля (моноширинный шрифт)."""

    def __init__(self, title, rows, color=KERNEL, width=None, size=17, row_h=0.36, pad=0.2):
        self.accent, self.fs, self.row_h = color, size, row_h
        self.title = code_line([(title, color)], size + 1)
        self.rows = VGroup(*[code_line([(r, TEXT)] if isinstance(r, str) else r, size) for r in rows])
        inner = max([self.title.width] + [r.width for r in self.rows])
        title_h = self.title.height + 0.18
        h = title_h + len(rows) * row_h + (0.14 if rows else 0)
        self.frame = tbox(width or inner + 2 * pad, h, color)
        top, left = self.frame.get_top()[1], self.frame.get_left()[0] + pad - 0.1
        self.title.move_to([0, top - title_h / 2, 0]).align_to([left, 0, 0], LEFT)
        parts = [self.frame, self.title]
        if rows:
            sep_y = top - title_h
            sep = Line([self.frame.get_left()[0], sep_y, 0], [self.frame.get_right()[0], sep_y, 0])
            parts.append(sep.set_stroke(color, 1.2, opacity=0.45))
            for i, r in enumerate(self.rows):
                r.move_to([0, sep_y - 0.07 - row_h * (i + 0.5), 0]).align_to([left, 0, 0], LEFT)
        super().__init__(*parts, self.rows)

    def row_box(self, i, color=None):
        color = color or self.accent
        box = RoundedRectangle(corner_radius=0.05, width=self.frame.width - 0.12, height=self.row_h - 0.03)
        box.set_fill(color, 0.22).set_stroke(color, 1.5, opacity=0.9)
        return box.move_to([self.frame.get_x(), self.rows[i].get_y(), 0])

    def anchor(self, i, side=RIGHT):
        """Точка на левом/правом краю карточки на высоте строки i."""
        edge = self.frame.get_right() if side is RIGHT else self.frame.get_left()
        return np.array([edge[0], self.rows[i].get_y(), 0])

    def new_row(self, i, content):
        row = code_line([(content, TEXT)] if isinstance(content, str) else content, self.fs)
        return row.move_to(self.rows[i]).align_to(self.rows[i], LEFT)


class Cells(VGroup):
    """Ряд или столбец одинаковых ячеек; подписи-индексы рядом с ячейками."""

    def __init__(self, n, w=0.9, h=0.42, direction=DOWN, color=PANEL_EDGE, fill=PANEL,
                 index=None, index_color=MUTED, index_size=15, gap=0.0, index_side=None):
        self.cells = VGroup(*[rbox(w, h, color, fill, r=0.06, sw=1.6) for _ in range(n)])
        self.cells.arrange(direction, buff=gap)
        parts = [self.cells]
        self.index = VGroup()
        if index is not None:
            side = index_side if index_side is not None else (LEFT if direction is DOWN else UP)
            for cell, label in zip(self.cells, index):
                self.index.add(mono(str(label), index_size, index_color).next_to(cell, side, buff=0.12))
            parts.append(self.index)
        self.items = [None] * n
        super().__init__(*parts)

    def put(self, i, content, color=TEXT, size=16):
        """Создать (не добавляя в сцену) содержимое ячейки i по её центру."""
        mob = code_line([(content, color)], size) if isinstance(content, str) else content
        if mob.width > self.cells[i].width - 0.08:
            mob.scale_to_fit_width(self.cells[i].width - 0.08)
        self.items[i] = mob.move_to(self.cells[i])
        return mob


class PageTable(VGroup):
    """Таблица страниц: виртуальная страница → фрейм, биты P (присутствует) и D (изменена)."""

    WIDTHS = (0.62, 0.92, 0.46, 0.46)

    def __init__(self, n=4, row_h=0.42, size=16, frames=None):
        heads = ("стр.", "фрейм", "P", "D")
        self.fs = size
        xs = np.cumsum((0,) + self.WIDTHS[:-1]) + np.array(self.WIDTHS) / 2
        header = VGroup(*[txt(h, 14, MUTED).move_to([x, 0, 0]) for h, x in zip(heads, xs)])
        self.rows, self.vals = VGroup(), []
        for i in range(n):
            y = -(i + 0.85) * row_h
            row = VGroup(*[rbox(w, row_h, PANEL_EDGE, PANEL, r=0.04, sw=1.4).move_to([x, y, 0])
                           for w, x in zip(self.WIDTHS, xs)])
            vals = [code_line([(str(i), MUTED)], size), code_line([("–", DIM)], size),
                    code_line([("0", DIM)], size), code_line([("0", DIM)], size)]
            for v, cell in zip(vals, row):
                v.move_to(cell)
            self.rows.add(row)
            self.vals.append(VGroup(*vals))
        super().__init__(header, self.rows, *self.vals)
        self.header = header
        if frames:
            for i, f in frames.items():
                self.set(i, frame=f, p=1, animate=False)

    def set(self, i, frame=None, p=None, d=None, animate=True):
        """Поменять значения строки i; возвращает список анимаций."""
        anims = []
        for col, value, color in ((1, frame, DATA), (2, p, GREEN if p else DIM), (3, d, DIRTY if d else DIM)):
            if value is None:
                continue
            old = self.vals[i][col]
            new = code_line([(str(value), color)], self.fs).move_to(self.rows[i][col])
            if animate:
                anims.append(Transform(old, new))
            else:
                old.become(new)
        return anims

    def row_box(self, i, color=YELLOW):
        box = SurroundingRectangle(self.rows[i], color=color, buff=0.04, corner_radius=0.06, stroke_width=3)
        return box.set_z_index(4)

    def anchor(self, i, side=RIGHT):
        edge = self.rows[i].get_right() if side is RIGHT else self.rows[i].get_left()
        return np.array([edge[0], self.rows[i].get_y(), 0])


# --------------------------------------------------------------- значки ---

def chip(label, color=HW, w=1.7, h=0.75, pins=6, size=16):
    """Микросхема контроллера с выводами сверху и снизу."""
    xs = np.linspace(-w / 2 + 0.22, w / 2 - 0.22, pins)
    legs = VGroup(*[Line([x, s * h / 2, 0], [x, s * (h / 2 + 0.13), 0]) for x in xs for s in (1, -1)])
    legs.set_stroke(color, 3 if h > 0.4 else 2)
    body = tbox(w, h, color, r=0.08, k=0.22)
    return VGroup(legs, body, mono(label, size, color).move_to(body)) if label else VGroup(legs, body)


def db9_icon(color=HW):
    """Разъём COM-порта (DB-9)."""
    shell = Polygon([-0.3, 0.14, 0], [0.3, 0.14, 0], [0.22, -0.14, 0], [-0.22, -0.14, 0])
    pins = VGroup(*[Dot([x, 0.04, 0], radius=0.028) for x in np.linspace(-0.18, 0.18, 5)],
                  *[Dot([x, -0.06, 0], radius=0.028) for x in np.linspace(-0.13, 0.13, 4)])
    return VGroup(shell.set_fill(tint(color, 0.2), 1).set_stroke(color, 2), pins.set_color(color))


def disk_icon(w=2.4, h=1.1, color=MUTED):
    """Цилиндр — накопитель."""
    eh = min(0.34, w * 0.28)
    fill = tint(color, 0.18)
    bottom = Ellipse(width=w, height=eh).set_fill(fill, 1).set_stroke(color, 2).shift(DOWN * h / 2)
    body = Rectangle(width=w, height=h).set_fill(fill, 1).set_stroke(width=0)
    sides = VGroup(Line([-w / 2, h / 2, 0], [-w / 2, -h / 2, 0]), Line([w / 2, h / 2, 0], [w / 2, -h / 2, 0]))
    sides.set_stroke(color, 2)
    top = Ellipse(width=w, height=eh).set_fill(tint(color, 0.32), 1).set_stroke(color, 2).shift(UP * h / 2)
    return VGroup(bottom, body, sides, top)


def file_icon(color=DATA, w=0.75, h=0.95):
    f = 0.24
    body = Polygon([-w / 2, h / 2, 0], [w / 2 - f, h / 2, 0], [w / 2, h / 2 - f, 0],
                   [w / 2, -h / 2, 0], [-w / 2, -h / 2, 0])
    body.set_fill(tint(color, 0.2), 1).set_stroke(color, 2.4)
    corner = Polygon([w / 2 - f, h / 2, 0], [w / 2 - f, h / 2 - f, 0], [w / 2, h / 2 - f, 0])
    corner.set_fill(color, 0.6).set_stroke(color, 2)
    lines = VGroup(*[Line([-w / 2 + 0.15, y, 0], [w / 2 - 0.15, y, 0]) for y in (0.0, -0.17, -0.34)])
    return VGroup(body, corner, lines.set_stroke(color, 2.4, opacity=0.6))


def ram_icon(color=USER, n=4, w=0.9):
    cells = VGroup(*[tbox(w, 0.2, color, r=0.03, k=0.25) for _ in range(n)]).arrange(DOWN, buff=0.06)
    return cells


class Monitor(VGroup):
    """Монитор с сеткой «пикселей»: self.px[row][col]."""

    def __init__(self, cols=16, rows=8, px=0.2, gap=0.03, color=MUTED):
        grid = VGroup(*[Square(px).set_fill("#0b0c0f", 1).set_stroke(width=0) for _ in range(cols * rows)])
        grid.arrange_in_grid(rows=rows, cols=cols, buff=gap)
        screen = rbox(grid.width + 0.3, grid.height + 0.3, color, "#07080a", r=0.1, sw=3).move_to(grid)
        neck = Rectangle(width=0.3, height=0.25).set_fill(tint(color, 0.4), 1).set_stroke(width=0)
        neck.next_to(screen, DOWN, buff=0)
        base = rbox(1.3, 0.1, color, tint(color, 0.4), r=0.05, sw=1.5).next_to(neck, DOWN, buff=0)
        super().__init__(neck, base, screen, grid)
        self.screen, self.grid = screen, grid
        self.px = [[grid[r * cols + c] for c in range(cols)] for r in range(rows)]


# --------------------------------------------------- стрелки и движение ---

def poly_arrow(*points, color=MUTED, sw=3, tip=0.17):
    """Ломаная стрелка через точки `points`; голова — заливной треугольник."""
    pts = [np.array(p, dtype=float) for p in points]
    d = normalize(pts[-1] - pts[-2])
    end = pts[-1].copy()
    pts[-1] = end - d * tip * 0.8
    line = VMobject().set_points_as_corners(pts).set_stroke(color, sw)
    n = np.array([-d[1], d[0], 0.0])
    head = Polygon(end, end - d * tip + n * tip * 0.55, end - d * tip - n * tip * 0.55)
    head.set_fill(color, 1).set_stroke(color, 1)
    return VGroup(line, head).set_z_index(3)


def grow(arrow, run_time=0.6):
    """Анимация «прорисовки» стрелки от начала к концу."""
    line, head = arrow
    return AnimationGroup(Create(line), FadeIn(head, rate_func=squish_rate_func(smooth, 0.7, 1.0)),
                          run_time=run_time)


def route(*points):
    """Невидимый путь для MoveAlongPath."""
    return VMobject().set_points_as_corners([np.array(p, dtype=float) for p in points])


def capsule(s, color, size=17, text_color=BG):
    """Цветная «капсула» — вызов или значение, которое перемещается по схеме."""
    label = code_line([(s, text_color)], size)
    pill = RoundedRectangle(corner_radius=(label.height + 0.1) / 2,
                            width=label.width + 0.18, height=label.height + 0.1)
    pill.set_fill(color, 1).set_stroke(width=0).move_to(label)
    return VGroup(pill, label).set_z_index(6)


def byte_box(ch, color=DATA, size=18, side=0.36):
    """Один байт данных: квадратик с символом."""
    box = RoundedRectangle(corner_radius=0.06, width=side, height=side)
    box.set_fill(tint(color, 0.45), 1).set_stroke(color, 2)
    return VGroup(box, code_line([(ch, TEXT)], size).move_to(box)).set_z_index(5)


def page_bytes(chars="BBBB", color=DATA):
    """Содержимое страницы — несколько байтов подряд (условно)."""
    return VGroup(*[byte_box(c, color, size=12, side=0.25) for c in chars]).arrange(RIGHT, buff=0.04)


def mode_badge(kernel=False):
    """Значок режима процессора в правом верхнем углу."""
    color = KERNEL if kernel else USER
    label = VGroup(Dot(radius=0.06, color=color),
                   txt("режим ядра" if kernel else "режим пользователя", 16, color)).arrange(RIGHT, buff=0.12)
    frame = rbox(label.width + 0.34, 0.4, color, tint(color, 0.12), r=0.2, sw=1.5).move_to(label)
    return VGroup(frame, label).to_corner(UR, buff=0.2)


def boundary(y, color=DIM, above=None, below=None, x0=-7.11, x1=7.11, size=15):
    """Пунктирная граница между уровнями (пользователь / ядро / оборудование)."""
    line = DashedLine([x0, y, 0], [x1, y, 0], dash_length=0.1, dashed_ratio=0.5).set_stroke(color, 1.8)
    parts = [line]
    if above:
        parts.append(txt(above, size, MUTED).move_to([x0 + 0.2, y + 0.2, 0], aligned_edge=LEFT))
    if below:
        parts.append(txt(below, size, MUTED).move_to([x0 + 0.2, y - 0.2, 0], aligned_edge=LEFT))
    return VGroup(*parts)


def flash(mob, color=YELLOW, buff=0.06, run_time=0.8, width=4):
    """Бегущий по контуру «огонёк» вокруг объекта."""
    rect = SurroundingRectangle(mob, color=color, buff=buff, corner_radius=0.1, stroke_width=width)
    return ShowPassingFlash(rect.set_z_index(7), time_width=0.5, run_time=run_time)
