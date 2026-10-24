"""01. Узел /dev/ttyS0 связывает имя устройства с драйвером."""
from manim import *

from base import BaseScene
from components import *
from style import *


class DevFilesScene(BaseScene):
    def construct(self):
        self.chapter("01", "Устройство выглядит как файл")

        terminal = CodePanel([
            [("$ ", GREEN), ("ls -l /dev/ttyS0", TEXT)],
            [("c", USER), ("rw-rw---- 1 root dialout  ", MUTED),
             ("4, 64", YELLOW), ("  /dev/ttyS0", TEXT)],
        ], title="терминал", size=25, width=10.7).move_to([0, 2.05, 0])
        self.play(FadeIn(terminal, shift=UP * 0.15), run_time=0.7)
        self.say("`/dev/ttyS0` – имя устройства в каталоге `/dev`", run_time=0.6)
        self.pause(0.8)

        node = VGroup(
            file_icon(USER, w=0.8, h=1.0),
            mono("/dev/ttyS0", 22, TEXT),
        ).arrange(DOWN, buff=0.22).move_to([-4.6, -0.35, 0])
        inode = Card("inode устройства", [
            [("тип      ", MUTED), ("c · символьное", USER)],
            [("i_rdev   ", MUTED), ("4:64", YELLOW)],
            [("данные    ", MUTED), ("не здесь", DIM)],
        ], color=KERNEL, width=4.25, size=19, row_h=0.44).move_to([-0.1, -0.35, 0])
        driver = VGroup(
            chip("UART", color=HW, w=1.65, h=0.65, size=20),
            txt("драйвер UART", 20, DRIVER),
        ).arrange(DOWN, buff=0.3).move_to([4.9, -0.35, 0])
        to_inode = poly_arrow(node.get_right() + RIGHT * 0.1,
                              inode.frame.get_left() + LEFT * 0.1, color=KERNEL)
        to_driver = poly_arrow(inode.frame.get_right() + RIGHT * 0.1,
                               driver.get_left() + LEFT * 0.1, color=DRIVER)

        self.say("Буква *c* означает символьное устройство",
                 FadeIn(node), FadeIn(inode), grow(to_inode), run_time=0.9)
        self.pause(0.9)
        self.say("Номер *4:64* помогает ядру найти драйвер",
                 grow(to_driver), FadeIn(driver), flash(inode.rows[1], YELLOW), run_time=0.9)
        self.pause(1.0)

        key = txt("Путь – это имя. Байты приходят через драйвер.", 29, TEXT, weight=BOLD)
        key.move_to([0, -2.55, 0])
        self.say("Байты приходят через драйвер", FadeIn(key), run_time=0.6)
        self.pause(1.3)
        self.clear_all()
