"""03. Жизненный цикл данных при чтении из последовательного порта."""
from manim import *

from base import BaseScene
from components import *
from style import *


class ReadScene(BaseScene):
    def construct(self):
        self.chapter("03", "read(): жизненный цикл данных")

        # Вызов и его результат находятся в памяти процесса.
        user_zone = RoundedRectangle(corner_radius=0.16, width=13.0, height=1.85)
        user_zone.set_fill(opacity=0).set_stroke(USER, width=1.4, opacity=0.55)
        user_zone.move_to([0, 2.25, 0]).set_z_index(-2)
        user_name = txt("процесс пользовательского уровня", 17, USER)
        user_name.move_to([0, 3.08, 0])
        user_name_bg = BackgroundRectangle(user_name, color=BG,
                                           fill_opacity=1, buff=0.12)
        levels = boundary(1.15, below="ядро Linux",
                          x0=-6.3, x1=6.3, size=16)

        code = CodePanel(["ssize_t n = read(fd, buf, 8);"],
                         size=23, width=7.1).move_to([-2.6, 2.25, 0])
        user_buf = Cells(3, w=0.54, h=0.54, direction=RIGHT,
                         gap=0.07, color=USER).move_to([4.7, 2.23, 0])
        user_label = mono("buf процесса", 18, USER)
        user_label.next_to(user_buf, UP, buff=0.13)

        # Три структуры ядра: число fd индексирует таблицу, а file хранит f_op.
        fdtable = Card("таблица дескрипторов", ["3 → struct file"],
                       color=USER, width=3.2, size=16, row_h=0.43)
        fdtable.move_to([-4.7, 0.17, 0])
        opened = Card("struct file", [[("f_op → ", MUTED), ("tty_fops", DRIVER)]],
                      width=2.85, size=18, row_h=0.45)
        opened.move_to([-1.35, 0.17, 0])
        tty = Card("TTY: file_operations",
                   [".read_iter → tty_read"], color=DRIVER,
                   width=3.65, size=16, row_h=0.45)
        tty.move_to([2.2, 0.17, 0])

        # UART может получить байты до вызова read() или пока тот ждёт данные.
        serial = Card("serial-драйвер", ["приём байтов"], color=DRIVER,
                      width=2.65, size=17, row_h=0.44)
        serial.move_to([2.7, -1.64, 0])
        uart = chip("UART", HW, w=1.55, h=0.68, size=20)
        uart.move_to([5.43, -1.64, 0])
        uart_label = txt("устройство", 16, HW).next_to(uart, DOWN, buff=0.18)
        kernel_buf = Cells(3, w=0.54, h=0.54, direction=RIGHT,
                           gap=0.07, color=KERNEL)
        kernel_buf.move_to([-1.05, -1.64, 0])
        kernel_label = mono("буфер TTY в ядре", 18, KERNEL)
        kernel_label.next_to(kernel_buf, UP, buff=0.13)

        request = VGroup(
            poly_arrow(code.frame.get_bottom() + DOWN * 0.03,
                       fdtable.frame.get_top() + UP * 0.03, color=USER),
            poly_arrow(fdtable.frame.get_right(), opened.frame.get_left(),
                       color=USER),
            poly_arrow(opened.frame.get_right(), tty.frame.get_left(),
                       color=DRIVER),
        )
        response = VGroup(
            poly_arrow(uart.get_left(), serial.frame.get_right(), color=DATA),
            poly_arrow(serial.frame.get_left(), kernel_buf.get_right(),
                       color=DATA),
        )

        self.play(FadeIn(user_zone), FadeIn(user_name_bg), FadeIn(user_name),
                  FadeIn(levels),
                  FadeIn(code), FadeIn(user_buf), FadeIn(user_label),
                  run_time=0.8)
        self.say("Программа вызывает `read(fd, buf, 8)`",
                 FadeIn(fdtable), grow(request[0]), run_time=0.8)
        self.say("`fd = 3` выбирает открытый `struct file`",
                 FadeIn(opened), grow(request[1]), run_time=0.8)
        self.say("`f_op` вызывает обработчик TTY `.read_iter`",
                 FadeIn(tty), grow(request[2]), run_time=0.8)

        # Убираем цепочку запроса до показа обратного потока данных.
        self.play(FadeOut(request), FadeIn(serial), FadeIn(uart),
                  FadeIn(uart_label), FadeIn(kernel_buf),
                  FadeIn(kernel_label), run_time=0.65)
        self.say("Если байтов ещё нет, `read()` ожидает данные",
                 flash(tty, DRIVER), run_time=0.65)
        self.say("UART принимает байты; serial-драйвер передаёт их TTY",
                 grow(response[0]), grow(response[1]), run_time=1.0)

        chars = ("O", "K", "\\n")
        in_kernel = VGroup(*[byte_box(c, DATA, size=15, side=0.38)
                             for c in chars])
        for item in in_kernel:
            item.move_to(uart.get_center())
        paths = [
            route(uart.get_center(), serial.frame.get_center(),
                  kernel_buf.cells[i].get_center())
            for i in range(3)
        ]
        self.say("Байты попадают в буфер TTY внутри ядра",
                 LaggedStart(*[MoveAlongPath(item, path)
                               for item, path in zip(in_kernel, paths)],
                             lag_ratio=0.19), run_time=1.3)

        # read() переносит полученные байты в пользовательский buf.
        # Скрываем уже объяснённую цепочку, освобождая путь для копирования.
        self.play(FadeOut(response), FadeOut(fdtable), FadeOut(opened),
                  FadeOut(tty), FadeOut(serial), FadeOut(uart),
                  FadeOut(uart_label), run_time=0.45)
        copy_arrow = poly_arrow(kernel_buf.get_right(),
                                user_buf.get_bottom(), color=DATA)
        in_user = in_kernel.copy()
        self.add(in_user)
        self.say("Ядро копирует байты в `buf` процесса",
                 grow(copy_arrow),
                 LaggedStart(*[item.animate.move_to(user_buf.cells[i])
                               for i, item in enumerate(in_user)],
                             lag_ratio=0.2), run_time=1.2)
        result = capsule("n = 3", USER, size=20)
        result.move_to([2.25, 2.23, 0])
        self.say("`read()` возвращает число прочитанных байтов: `n = 3`",
                 FadeIn(result), run_time=0.7)
        self.pause(0.8)
        self.clear_all()
