"""06. Условный пример: драйвер /dev/fb0 отображает видеопамять."""
from manim import *

from base import BaseScene
from components import *
from style import *


HEART = (
    "...XXX...XXX....",
    "..XXXXX.XXXXX...",
    ".XXXXXXXXXXXXX..",
    ".XXXXXXXXXXXXX..",
    "..XXXXXXXXXXX...",
    "...XXXXXXXXX....",
    ".....XXXXX......",
    ".......X........",
)


class FramebufferScene(BaseScene):
    def construct(self):
        self.chapter("06", "Когда mmap поддерживает драйвер")

        lines = [
            'fd = open("/dev/fb0", O_RDWR);',
            "ioctl(fd, FBIOGET_VSCREENINFO, &vi);",
            "fb = mmap(NULL, size, PROT_WRITE, MAP_SHARED, fd, 0);",
            "fb[pixel] = color;",
        ]
        code = CodePanel(lines, size=19, width=10.4).move_to([-1.5, 2.25, 0])
        memory = Card("память процесса", ["fb[pixel]"], color=USER,
                      width=3.15, size=20, row_h=0.54).move_to([-5.15, -0.45, 0])
        driver = Card("драйвер fbdev", [".ioctl()", ".mmap()"], color=DRIVER,
                      width=2.85, size=20, row_h=0.48).move_to([-1.85, -0.45, 0])
        vram = Card("видеопамять", ["пиксели VRAM"], color=HW,
                    width=2.65, size=20, row_h=0.54).move_to([1.35, -0.45, 0])
        monitor = Monitor(16, 8, px=0.18, gap=0.025, color=MUTED)
        monitor.move_to([4.9, -0.45, 0])
        label = txt("экран", 19, MUTED).next_to(monitor, DOWN, buff=0.12)
        map_links = (
            poly_arrow(memory.frame.get_right(), driver.frame.get_left(), color=USER, sw=3.5),
            poly_arrow(driver.frame.get_right(), vram.frame.get_left(), color=DRIVER, sw=3.5),
        )
        video_link = poly_arrow(vram.frame.get_right(), monitor.screen.get_left(),
                                color=HW, sw=3.5)
        condition = txt("если драйвер реализовал .mmap()", 21, DRIVER)
        condition.move_to([0, -2.45, 0])

        self.play(FadeIn(code), FadeIn(memory), FadeIn(driver), FadeIn(vram),
                  FadeIn(monitor), FadeIn(label), self.show_mode(), run_time=0.8)
        self.say("`/dev/fb0` – пример устройства с видеопамятью",
                 run_time=0.6)
        self.pause(0.6)

        info = capsule("размер и формат", DRIVER, size=17).move_to(code.lines[1])
        self.say("`ioctl` узнаёт размер и формат экрана",
                 MoveAlongPath(info, route(info.get_center(), driver.rows[0].get_center())),
                 self.mode(True), run_time=0.9)
        self.play(FadeOut(info), flash(driver.rows[0], DRIVER), run_time=0.5)

        call = capsule("mmap()", USER, size=18).move_to(code.lines[2])
        self.say("Драйвер связывает адреса с видеопамятью",
                 MoveAlongPath(call, route(call.get_center(), driver.rows[1].get_center())),
                 FadeIn(condition), flash(driver.rows[1], DRIVER), run_time=1.0)
        self.play(FadeOut(call), grow(map_links[0]), grow(map_links[1]),
                  grow(video_link), self.mode(False), run_time=0.8)
        self.pause(0.8)

        pixel = capsule("fb[pixel] = color", USER, size=17).move_to(code.lines[3])
        self.say("Запись в `fb` меняет пиксели экрана",
                 MoveAlongPath(pixel, route(pixel.get_center(), memory.frame.get_center(),
                                            vram.frame.get_center())), run_time=1.0)
        self.play(FadeOut(pixel), run_time=0.2)
        rows = []
        for r in range(8):
            color = interpolate_color(ManimColor(PINK), ManimColor(ORANGE), r / 7)
            rows.append(AnimationGroup(*[
                px.animate.set_fill(color if HEART[r][c] == "X" else "#1d2a44", 1)
                for c, px in enumerate(monitor.px[r])
            ]))
        self.play(LaggedStart(*rows, lag_ratio=0.14), run_time=2.0)
        self.pause(1.0)

        self.clear_stage(run_time=0.45)
        title = txt("Три маршрута доступа", 34, TEXT, weight=BOLD).move_to([0, 2.25, 0])
        items = VGroup(
            Card("read() устройства", ["fd → драйвер → buf"], color=DRIVER,
                 width=5.1, size=20, row_h=0.58),
            Card("mmap() файла", ["fault → кэш → память"], color=DATA,
                 width=5.1, size=20, row_h=0.58),
            Card("mmap() устройства", ["драйвер → память устройства"], color=HW,
                 width=5.1, size=20, row_h=0.58),
        ).arrange(DOWN, buff=0.2).move_to([0, -0.25, 0])
        self.say("Путь данных зависит от файла и драйвера",
                 FadeIn(title), LaggedStart(*[FadeIn(item, shift=RIGHT * 0.2)
                                              for item in items], lag_ratio=0.25), run_time=1.2)
        self.pause(1.6)
        self.clear_all()
