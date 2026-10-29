"""01. Имя /dev/ttyS0, номер устройства и запись VFS в ядре Linux."""
from manim import *

from base import BaseScene
from components import *
from style import *


class DevFilesScene(BaseScene):
    def construct(self):
        self.chapter("01", "Узел устройства в /dev")

        terminal = CodePanel([
            [("$ ", GREEN), ("ls -l /dev/ttyS0", TEXT)],
            [("c", USER), ("rw-rw---- 1 root dialout  ", MUTED),
             ("4, 64", YELLOW), ("  /dev/ttyS0", TEXT)],
        ], title="терминал", size=25, width=10.7).move_to([0, 0.7, 0])
        self.play(FadeIn(terminal, shift=UP * 0.15), run_time=0.7)
        self.say("`/dev/ttyS0` – путь к узлу устройства", run_time=0.6)
        self.say("Буква *c* означает символьное устройство",
                 flash(terminal.lines[1].text[0], USER), run_time=0.8)
        self.clear_stage(run_time=0.45)

        # Рамка связывает VFS и tty со структурами ядра, а UART оставляет снаружи.
        kernel_box = rbox(7.45, 3.2, KERNEL, BG, r=0.16, sw=1.8)
        kernel_box.move_to([0, -0.55, 0]).set_z_index(-1)
        kernel_label = txt("ядро Linux", 20, KERNEL, weight=BOLD)
        kernel_label.move_to([0, 0.78, 0])
        kernel = VGroup(kernel_box, kernel_label)

        node = VGroup(
            file_icon(USER, w=0.8, h=1.0),
            mono("/dev/ttyS0", 21, TEXT),
        ).arrange(DOWN, buff=0.18).move_to([-5.15, -0.4, 0])
        inode = Card("VFS: inode", [
            [("тип       ", MUTED), ("c", USER)],
            [("i_rdev    ", MUTED), ("4:64", YELLOW)],
        ], color=KERNEL, width=3.15, size=19, row_h=0.44)
        inode.move_to([-1.92, -0.25, 0])
        tty = Card("tty / serial", ["порт ttyS0"], color=DRIVER,
                   width=2.7, size=19, row_h=0.5).move_to([1.9, -0.25, 0])
        uart = VGroup(chip("UART", color=HW, w=1.65, h=0.65, size=20),
                      txt("устройство", 17, HW)).arrange(DOWN, buff=0.18)
        uart.move_to([5.25, -0.4, 0])

        to_inode = poly_arrow(node.get_right() + RIGHT * 0.08,
                              inode.frame.get_left() + LEFT * 0.08, color=KERNEL)
        to_tty = poly_arrow(inode.frame.get_right() + RIGHT * 0.08,
                            tty.frame.get_left() + LEFT * 0.08, color=DRIVER)
        to_uart = poly_arrow(tty.frame.get_right() + RIGHT * 0.08,
                             uart.get_left() + LEFT * 0.08, color=HW)

        number_lines = VGroup(
            mono("4 = major: TTY", 17, YELLOW),
            mono("64 = minor: ttyS0", 17, YELLOW),
        ).arrange(DOWN, buff=0.12).move_to([-1.92, -1.5, 0])

        self.say("VFS ядра хранит запись об узле",
                 FadeIn(node), FadeIn(kernel), FadeIn(inode), grow(to_inode), run_time=0.9)
        self.say("`i_rdev` хранит номер устройства `4:64`",
                 flash(inode.rows[1], YELLOW), FadeIn(number_lines), run_time=0.9)
        self.say("*4:64* – номер, не адрес: 4 = TTY, 64 = ttyS0",
                 flash(number_lines, YELLOW), run_time=0.9)
        self.say("Номер ведёт к tty/serial, а тот работает с UART",
                 FadeIn(tty), FadeIn(uart), grow(to_tty), grow(to_uart), run_time=1.0)
        self.pause(0.7)
        self.clear_all()
