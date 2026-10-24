"""Палитра, шрифты и общие константы оформления.

Стиль по мотивам Core Dumped: тёмный фон, плоские блоки со скруглёнными углами,
тонированная заливка в цвет обводки, один цвет на каждую «роль» сущности.
"""
import manimpango


def _pick_font(*candidates: str) -> str:
    """Первый установленный шрифт из списка (на Linux/macOS подойдут запасные)."""
    installed = set(manimpango.list_fonts())
    for name in candidates:
        if name in installed:
            return name
    return candidates[-1]


SANS = _pick_font("Segoe UI", "Inter", "PT Sans", "Noto Sans", "DejaVu Sans")
MONO = _pick_font("Cascadia Mono", "JetBrains Mono", "Consolas", "DejaVu Sans Mono")

# Фон и нейтральные цвета
BG = "#101216"
PANEL = "#191c22"
PANEL_EDGE = "#2c313b"
TEXT = "#e6e8ec"
MUTED = "#8b93a1"
DIM = "#4b5260"

# Акценты
BLUE = "#5ab0f6"
CYAN = "#4fd1c5"
GREEN = "#7ee081"
YELLOW = "#ffd166"
ORANGE = "#ff9f43"
RED = "#ff5c6c"
PURPLE = "#b48ef5"
PINK = "#ff8fc7"

# Цвет = роль сущности (держим одинаковым во всех сценах)
USER = BLUE      # процесс, пространство пользователя
KERNEL = PURPLE  # структуры и код ядра
DRIVER = CYAN    # драйвер устройства (тоже код ядра, но свой для устройства)
HW = ORANGE      # оборудование
DATA = GREEN     # данные файла, страницы кэша
FAULT = RED      # page fault, ошибки
DIRTY = YELLOW   # изменённые («грязные») данные

# Подсветка синтаксиса C (близко к теме Material Palenight)
SYNTAX = {
    "kw": "#c792ea",
    "fn": "#82aaff",
    "str": "#c3e88d",
    "num": "#f78c6c",
    "const": "#ffcb6b",
    "com": "#6c7693",
    "punct": "#89ddff",
    "text": "#d6deeb",
}

AUTHORS = "Иванов · Гусев · 3211"

# Небольшие паузы между действиями и минимальное время чтения каждого тезиса.
PAUSE = 1.0
MIN_CAPTION_HOLD = 1.7

CAPTION_Y = -3.58
CAPTION_SIZE = 24
