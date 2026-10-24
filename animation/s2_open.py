"""02. open: имя устройства превращается в файловый дескриптор."""
from manim import *

from base import BaseScene
from components import *
from style import *


class OpenScene(BaseScene):
    def construct(self):
        self.chapter("02", "open(): путь → дескриптор")

        src = 'int fd = open("/dev/ttyS0", O_RDWR);'
        code = CodePanel([src], size=24, width=8.9).move_to([-1.5, 2.45, 0])
        path = Card("путь", ["/dev/ttyS0"], color=USER, width=2.5,
                    size=20, row_h=0.48).move_to([-5.2, 0.55, 0])
        vfs = Card("VFS", ["найти inode"], color=KERNEL, width=2.5,
                   size=20, row_h=0.48).move_to([-1.8, 0.55, 0])
        driver = Card("драйвер tty", [".open()", ".read()"], color=DRIVER,
                      width=2.65, size=20, row_h=0.44).move_to([1.75, 0.55, 0])
        uart = VGroup(chip("UART", HW, w=1.65, h=0.7, size=20),
                      txt("порт", 18, MUTED)).arrange(DOWN, buff=0.15)
        uart.move_to([5.3, 0.55, 0])
        forward = [
            poly_arrow(path.frame.get_right(), vfs.frame.get_left(), color=KERNEL),
            poly_arrow(vfs.frame.get_right(), driver.frame.get_left(), color=DRIVER),
            poly_arrow(driver.frame.get_right(), uart.get_left(), color=HW),
        ]

        table = Cells(4, w=1.55, h=0.42, index=range(4))
        table.shift(np.array([-4.85, -1.75, 0]) - table.cells.get_center())
        table.add(*[table.put(i, label, MUTED, 17) for i, label in
                    enumerate(("stdin", "stdout", "stderr"))])
        table.add(txt("таблица fd процесса", 18, MUTED).next_to(table.cells, UP, buff=0.15))
        opened = Card("struct file", [[("f_op → ", MUTED), ("tty_fops", DRIVER)]],
                      width=3.1, size=20, row_h=0.48).move_to([-0.35, -1.75, 0])
        fd_link = poly_arrow(table.cells[3].get_right(), opened.frame.get_left(), color=USER)
        ops_link = poly_arrow(opened.frame.get_right(),
                              [driver.frame.get_x(), driver.frame.get_bottom()[1] - 0.05, 0],
                              color=DRIVER)

        self.play(FadeIn(code), FadeIn(path), self.show_mode(), run_time=0.8)
        self.say("`open()` передаёт ядру имя устройства",
                 FadeIn(vfs), grow(forward[0]), self.mode(True), run_time=0.8)
        self.pause(0.8)

        self.say("По номеру узла ядро вызывает *драйвер*",
                 FadeIn(driver), grow(forward[1]), run_time=0.9)
        self.play(FadeIn(uart), grow(forward[2]), flash(uart[0], HW), run_time=0.8)
        self.pause(0.8)

        self.say("`struct file` хранит функции драйвера",
                 FadeIn(opened, shift=UP * 0.15), grow(ops_link), run_time=0.9)
        self.play(FadeIn(table), run_time=0.5)
        third = table.put(3, "file", USER, 18)
        self.say("Ссылка на файл попадает в таблицу процесса",
                 FadeIn(third), grow(fd_link), flash(table.cells[3], USER), run_time=0.9)
        self.pause(0.7)

        self.say("*fd = 3* – номер ячейки, а не адрес устройства",
                 flash(table.cells[3], USER), self.mode(False), run_time=0.9)
        self.pause(1.2)
        self.clear_all()
