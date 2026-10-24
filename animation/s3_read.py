"""03. read: один вызов, две границы и байты в буфере процесса."""
from manim import *

from base import BaseScene
from components import *
from style import *


class ReadScene(BaseScene):
    def construct(self):
        self.chapter("03", "read(): путь данных")

        src = "ssize_t n = read(fd, buf, 8);"
        code = CodePanel([src], size=24, width=7.3).move_to([-2.65, 2.6, 0])
        user_buf = Cells(3, w=0.52, h=0.52, direction=RIGHT, gap=0.06, color=USER)
        user_buf.move_to([4.75, 2.45, 0])
        user_label = mono("buf процесса", 19, USER).next_to(user_buf, UP, buff=0.15)
        upper = boundary(1.45, above="пользователь", below="ядро", x0=-6.8, x1=6.8)

        fd = Card("fd = 3", ["таблица fd"], color=USER,
                  width=2.45, size=19, row_h=0.47).move_to([-5.15, 0.25, 0])
        opened = Card("struct file", [[("f_op → ", MUTED), ("tty_fops", DRIVER)]],
                      width=3.1, size=19, row_h=0.47).move_to([-1.7, 0.25, 0])
        driver = Card("драйвер tty", [".read()"], color=DRIVER,
                      width=2.55, size=19, row_h=0.47).move_to([2.0, 0.25, 0])
        lookup = [poly_arrow(fd.frame.get_right(), opened.frame.get_left(), color=USER),
                  poly_arrow(opened.frame.get_right(), driver.frame.get_left(), color=DRIVER)]

        kernel_buf = Cells(3, w=0.52, h=0.52, direction=RIGHT, gap=0.06, color=KERNEL)
        kernel_buf.move_to([1.8, -1.4, 0])
        kernel_label = mono("буфер ядра", 19, KERNEL).next_to(kernel_buf, UP, buff=0.13)
        uart = chip("UART", HW, w=1.7, h=0.7, size=21).move_to([5.15, -1.4, 0])
        uart_label = txt("устройство", 18, HW).next_to(uart, DOWN, buff=0.18)

        self.play(FadeIn(code), FadeIn(user_buf), FadeIn(user_label), FadeIn(upper),
                  FadeIn(fd), self.show_mode(), run_time=0.9)
        self.say("`read(fd, buf, 8)` просит до 8 байтов", run_time=0.6)
        self.pause(0.6)

        call = capsule("read()", USER, size=19).move_to(code.lines[0])
        self.say("`fd` приводит к функции `.read()` драйвера",
                 MoveAlongPath(call, route(call.get_center(), fd.frame.get_top())),
                 FadeIn(opened), FadeIn(driver), self.mode(True),
                 grow(lookup[0]), grow(lookup[1]), run_time=1.0)
        self.play(FadeOut(call), flash(driver, DRIVER), run_time=0.5)
        self.pause(0.7)

        self.play(FadeIn(kernel_buf), FadeIn(kernel_label), FadeIn(uart),
                  FadeIn(uart_label), run_time=0.7)

        chars = ("O", "K", "\\n")
        arriving = VGroup(*[byte_box(ch, DATA, size=16, side=0.39) for ch in chars])
        for item in arriving:
            item.move_to(uart)
        paths = [route(uart.get_center(),
                       [kernel_buf.cells[i].get_x(), uart.get_y(), 0],
                       kernel_buf.cells[i].get_center()) for i in range(3)]
        self.say("От UART байты попадают в *буфер ядра*",
                 LaggedStart(*[MoveAlongPath(item, path) for item, path in zip(arriving, paths)],
                             lag_ratio=0.22), run_time=1.5)
        self.pause(0.6)

        copies = arriving.copy()
        self.add(copies)
        self.say("Ядро копирует байты в *buf процесса*",
                 LaggedStart(*[item.animate.move_to(user_buf.cells[i])
                               for i, item in enumerate(copies)], lag_ratio=0.2),
                 run_time=1.2)
        self.pause(0.7)

        result = capsule("n = 3", USER, size=21).move_to(driver.frame.get_top())
        self.say("Пришло 3 байта, поэтому `n = 3`",
                 MoveAlongPath(result, route(result.get_center(),
                                             [user_buf.get_x(), 1.9, 0])),
                 self.mode(False), run_time=0.9)
        self.pause(0.9)

        self.clear_stage(run_time=0.4)
        heading = txt("Один интерфейс – разные реализации", 32, TEXT, weight=BOLD)
        heading.move_to([0, 2.0, 0])
        left = Card("read(fd, buf, n)", ["/dev/ttyS0 → драйвер tty"],
                    color=DRIVER, width=5.0, size=21, row_h=0.58).move_to([-3.15, 0.1, 0])
        right = Card("read(fd, buf, n)", ["data.bin → файловая система"],
                     color=DATA, width=5.3, size=21, row_h=0.58).move_to([3.15, 0.1, 0])
        self.say("Один `read()` – разные пути чтения",
                 FadeIn(heading), FadeIn(left), FadeIn(right), run_time=0.7)
        self.pause(1.4)
        self.clear_all()
