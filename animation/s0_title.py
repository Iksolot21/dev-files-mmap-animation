"""Фрагмент 0. Титульный кадр."""
from manim import *

from base import BaseScene
from components import *
from style import *


class TitleScene(BaseScene):
    def construct(self):
        device = chip("UART", w=1.5, h=0.8)
        file = file_icon(DATA, w=0.85, h=1.05)
        memory = ram_icon(USER, n=5, w=1.0)
        icons = VGroup(device, file, memory).arrange(RIGHT, buff=1.6).shift(UP * 1.75)
        links = VGroup(
            DashedLine(device.get_right(), file.get_left(), buff=0.25, dash_length=0.1),
            DashedLine(file.get_right(), memory.get_left(), buff=0.25, dash_length=0.1),
        ).set_stroke(DIM, 3)
        captions = VGroup(*[txt(s, 17, MUTED).next_to(icon, DOWN, buff=0.25)
                            for s, icon in zip(("устройство", "файл", "память"), icons)])
        captions.align_to(captions[1], DOWN)

        title = txt("Устройства как файлы", 52, TEXT, weight=BOLD).shift(DOWN * 0.15)
        subtitle = txt("и отображение файлов в память", 34, MUTED).next_to(title, DOWN, buff=0.22)
        tags = mono("open · read · ioctl · mmap · page fault", 21, BLUE).next_to(subtitle, DOWN, buff=0.5)
        authors = txt(AUTHORS, 19, DIM).to_edge(DOWN, buff=0.45)

        self.play(LaggedStart(*[FadeIn(i, shift=UP * 0.3) for i in icons], lag_ratio=0.25), run_time=1.0)
        self.play(Create(links), FadeIn(captions), run_time=0.5)
        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(subtitle, shift=UP * 0.15), FadeIn(tags, shift=UP * 0.15), FadeIn(authors), run_time=0.6)
        self.pause(1.4)
        self.clear_all()
