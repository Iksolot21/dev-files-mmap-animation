"""Фрагмент 4: отображение обычного файла и первый доступ к его странице."""
from manim import *

from base import BaseScene
from components import CodePanel, capsule, grow, mono, poly_arrow, tbox, txt
from style import *


# Сцена 6 использует эту высоту для четырёх страниц видеопамяти.
PAGE_H = 0.38


def mmap_panel(title, color, x, y=0.05, w=3.35, h=2.25):
    """Крупная карточка для файла, виртуального диапазона или кэша страниц."""
    frame = tbox(w, h, color, k=0.13).move_to([x, y, 0])
    heading = txt(title, 21, color, weight=BOLD)
    heading.move_to([x, frame.get_top()[1] - 0.38, 0])
    return VGroup(frame, heading)


def mmap_page_cell(label, color, filled=True):
    box = tbox(0.52, 0.56, color, r=0.07, k=0.25 if filled else 0.06)
    if not filled:
        box.set_fill(PANEL, 1).set_stroke(color, 1.6, opacity=0.65)
    return VGroup(box, mono(label, 20, color).move_to(box))


class MmapScene(BaseScene):
    def construct(self):
        self.chapter("04", "mmap(): файл как память")

        source = [
            'fd = open("data.bin", O_RDONLY);',
            'p = mmap(NULL, 16384, PROT_READ, MAP_SHARED, fd, 0);',
            'char c = p[5000];',
        ]
        code = CodePanel(source, title="процесс · обычный файл", size=18, width=10.2)
        code.move_to([-1.0, 2.45, 0])

        file_panel = mmap_panel("файл · data.bin", DATA, -4.75)
        file_pages = VGroup(*[mmap_page_cell(c, DATA) for c in "ABCD"])
        file_pages.arrange(RIGHT, buff=0.11).move_to([-4.75, -0.35, 0])
        file_hint = txt("4 страницы по 4 КиБ", 17, MUTED).move_to([-4.75, 0.25, 0])

        vma_panel = mmap_panel("VMA процесса", USER, 0)
        vma_info = mono("p → data.bin", 18, USER).move_to([0, 0.36, 0])
        virtual_pages = VGroup(*[mmap_page_cell(str(i), USER, filled=False) for i in range(4)])
        virtual_pages.arrange(RIGHT, buff=0.12).move_to([0, -0.32, 0])

        cache_panel = mmap_panel("кэш страниц · RAM", DATA, 4.75)
        empty_label = txt("страницы B здесь нет", 17, MUTED).move_to([4.75, -0.05, 0])
        cache_page = mmap_page_cell("B", DATA).scale(1.32).move_to([4.75, -0.12, 0])
        cache_note = txt("страница файла в памяти", 16, DATA).move_to([4.75, -0.7, 0])

        self.play(FadeIn(code), FadeIn(file_panel), FadeIn(file_pages), FadeIn(file_hint),
                  self.show_mode(), run_time=0.9)

        # mmap устанавливает соответствие диапазона файлу; страница ещё не загружена.
        map_highlight = code.highlight(1)
        self.say("`mmap` связывает адреса с открытым `data.bin`",
                 FadeIn(map_highlight), FadeIn(vma_panel), FadeIn(vma_info),
                 LaggedStart(*[FadeIn(page, scale=0.85) for page in virtual_pages], lag_ratio=0.12),
                 run_time=0.9)
        no_io = capsule("без загрузки страниц", KERNEL, size=16).move_to([4.75, -1.55, 0])
        self.say("Данные пока не загружены в память",
                 FadeIn(cache_panel), FadeIn(empty_label),
                 FadeIn(no_io, shift=UP * 0.15), run_time=0.55)
        self.pause(0.8)

        # p[5000] относится ко второй странице. На первом доступе возникает fault.
        read_highlight = code.highlight(2)
        chosen = SurroundingRectangle(virtual_pages[1], color=FAULT, buff=0.05,
                                      corner_radius=0.08, stroke_width=3)
        access = capsule("p[5000]", USER, size=18).move_to([0, -1.55, 0])
        self.say("`p[5000]` обращается ко второй странице",
                 Transform(map_highlight, read_highlight), FadeIn(access), FadeIn(chosen),
                 run_time=0.7)
        fault = capsule("page fault", FAULT, size=18).move_to([0, -1.55, 0])
        self.say("Страницы нет: возникает *page fault*",
                 ReplacementTransform(access, fault), self.mode(True),
                 run_time=0.6, accent=FAULT)
        self.pause(0.45)

        # При промахе кэша ядро получает страницу файла и помещает её в RAM.
        loading = file_pages[1].copy().set_z_index(8)
        path = CubicBezier(file_pages[1].get_bottom() + DOWN * 0.06,
                           [-3.0, -2.45, 0], [3.0, -2.45, 0],
                           cache_page.get_center())
        loading.move_to(path.get_start())
        self.say("Ядро загружает страницу в память",
                 FadeIn(loading), FadeOut(no_io), FadeOut(empty_label), run_time=0.55)
        self.play(MoveAlongPath(loading, path), run_time=1.3)
        self.play(ReplacementTransform(loading, cache_page), FadeIn(cache_note),
                  run_time=0.55)
        self.pause(0.55)

        mapped = mmap_page_cell("1", USER).move_to(virtual_pages[1])
        link = poly_arrow(vma_panel.get_right() + RIGHT * 0.06,
                          cache_panel.get_left() + LEFT * 0.06, color=DATA)
        result = mono("c = 'B'", 22, DATA).move_to([0, -1.65, 0])
        self.say("После fault чтение страницы в RAM возвращает B",
                 ReplacementTransform(fault, result), FadeOut(chosen),
                 ReplacementTransform(virtual_pages[1], mapped), grow(link),
                 self.mode(False), run_time=0.85)
        self.pause(0.65)

        # Следующее чтение уже использует созданное отображение.
        next_read = capsule("p[5001]", USER, size=18).move_to([0, -1.65, 0])
        self.say("Повторное чтение идёт без нового fault",
                 FadeOut(result), FadeIn(next_read),
                 Flash(cache_page, color=DATA, flash_radius=0.7), run_time=0.9)
        self.pause(1.0)
        self.clear_all()
