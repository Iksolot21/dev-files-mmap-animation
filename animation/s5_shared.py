"""Фрагмент 5: общая запись, синхронизация и личная копия MAP_PRIVATE."""
from manim import *

from base import BaseScene
from components import capsule, grow, mono, poly_arrow, tbox, txt
from style import *


def shared_card(title, color, x, y=0.1, w=3.55, h=2.25):
    frame = tbox(w, h, color, k=0.14).move_to([x, y, 0])
    heading = txt(title, 21, color, weight=BOLD)
    heading.move_to([x, frame.get_top()[1] - 0.4, 0])
    return VGroup(frame, heading)


def shared_value(value, color, x, y=-0.2):
    cell = tbox(1.05, 0.72, color, k=0.28).move_to([x, y, 0])
    glyph = mono(value, 32, color, weight=BOLD).move_to(cell)
    return VGroup(cell, glyph)


class SharedScene(BaseScene):
    def construct(self):
        self.chapter("05", "MAP_SHARED и MAP_PRIVATE")

        a = shared_card("процесс A", USER, -4.8)
        b = shared_card("процесс B", USER, 4.8)
        ram = shared_card("общая страница · RAM", DATA, 0)
        a_mode = mono("MAP_SHARED", 19, USER).move_to([-4.8, 0.22, 0])
        b_mode = mono("MAP_SHARED", 19, USER).move_to([4.8, 0.22, 0])
        a_code = mono("p[5000] = 'X'", 17, TEXT).move_to([-4.8, -0.42, 0])
        b_code = mono("q[5000] → ?", 18, TEXT).move_to([4.8, -0.42, 0])
        page_b = shared_value("B", DATA, 0, -0.2)

        disk = tbox(4.4, 0.72, DATA, k=0.08).move_to([0, -1.95, 0])
        disk_label = mono("data.bin : B", 21, DATA).move_to(disk)
        file_group = VGroup(disk, disk_label)
        a_to_ram = poly_arrow(a.get_right() + RIGHT * 0.06,
                              ram.get_left() + LEFT * 0.06, color=DATA)
        ram_to_b = poly_arrow(ram.get_right() + RIGHT * 0.06,
                              b.get_left() + LEFT * 0.06, color=DATA)

        self.play(FadeIn(a), FadeIn(b), FadeIn(ram), FadeIn(a_mode), FadeIn(b_mode),
                  FadeIn(a_code), FadeIn(b_code), FadeIn(page_b), FadeIn(file_group),
                  grow(a_to_ram), grow(ram_to_b), run_time=1.0)
        self.pause(0.7)

        # Общая запись видна другому отображению ещё до записи страницы на диск.
        write_x = capsule("'X'", DIRTY, size=20).move_to(a_code)
        dirty = capsule("изменена", DIRTY, size=16).move_to([0, -1.03, 0])
        page_x = shared_value("X", DIRTY, 0, -0.2)
        self.say("A меняет байт B на X в общей странице", FadeIn(write_x),
                 run_time=0.5)
        self.play(write_x.animate.move_to(page_b), run_time=0.65)
        self.play(FadeOut(write_x), ReplacementTransform(page_b, page_x),
                  FadeIn(dirty), run_time=0.5)

        b_result = mono("q[5000] → 'X'", 18, DATA).move_to(b_code)
        self.say("B уже видит X; на диске пока B",
                 ReplacementTransform(b_code, b_result),
                 Flash(page_x, color=DIRTY, flash_radius=0.7), run_time=0.75)
        self.pause(0.7)

        # MS_SYNC дожидается записи грязной страницы в файл.
        sync_label = capsule("msync(MS_SYNC)", KERNEL, size=17).move_to([3.3, -1.95, 0])
        writeback = poly_arrow(page_x.get_bottom() + DOWN * 0.08,
                               disk.get_top() + UP * 0.08, color=DIRTY)
        self.say("`msync` записывает изменение в файл",
                 FadeIn(sync_label), grow(writeback), run_time=0.8)
        disk_x = mono("data.bin : X", 21, DATA).move_to(disk)
        self.play(ReplacementTransform(disk_label, disk_x), FadeOut(dirty),
                  FadeOut(sync_label), run_time=0.6)
        self.pause(0.25)

        # Три карточки и надпись MAP_PRIVATE объясняют переход без отдельной подписи.
        self.clear_stage(run_time=0.5)
        self.hold_caption()
        self.remove(self.caption)
        self.caption = None
        self.caption_visible_at = None

        file_private = shared_card("файл · data.bin", DATA, -4.8)
        file_x = shared_value("X", DATA, -4.8, -0.2)
        cache_private = shared_card("общая страница · A", DATA, 0)
        cache_x = shared_value("X", DATA, 0, -0.2)
        private = shared_card("личная копия · B", PINK, 4.8)
        private_empty = txt("пока нет копии", 18, MUTED).move_to([4.8, -0.15, 0])
        private_mode = mono("MAP_PRIVATE", 20, PINK).move_to([4.8, -1.4, 0])
        command = mono("q[5000] = 'Y'", 21, TEXT).move_to([4.8, -1.9, 0])

        self.play(FadeIn(file_private), FadeIn(file_x), FadeIn(cache_private),
                  FadeIn(cache_x), FadeIn(private), FadeIn(private_empty),
                  FadeIn(private_mode), FadeIn(command), run_time=0.7)

        copy_arrow = poly_arrow(cache_private.get_right() + RIGHT * 0.06,
                                private.get_left() + LEFT * 0.06, color=PINK)
        copied_x = shared_value("X", PINK, 4.8, -0.2)
        copied_y = shared_value("Y", PINK, 4.8, -0.2)
        self.say("B пишет Y в личную копию; A и файл сохраняют X",
                 grow(copy_arrow), ReplacementTransform(private_empty, copied_x),
                 run_time=0.8)
        self.play(ReplacementTransform(copied_x, copied_y),
                  Flash(copied_y, color=PINK, flash_radius=0.7), run_time=0.8)
        self.pause(0.2)
        self.clear_all(run_time=0.45)
