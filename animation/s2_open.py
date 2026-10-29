"""02. open: разрешение пути, обработчик TTY и дескриптор процесса."""
from manim import *

from base import BaseScene
from components import *
from style import *


class OpenScene(BaseScene):
    def construct(self):
        self.chapter("02", "open(): инициализация подключения")

        # Код и возвращённое число принадлежат процессу. Таблица дескрипторов,
        # struct file и обработчики TTY находятся в ядре Linux.
        user_zone = RoundedRectangle(corner_radius=0.16, width=13.0, height=1.9)
        user_zone.set_fill(opacity=0).set_stroke(USER, width=1.4, opacity=0.5)
        user_zone.move_to([0, 2.2, 0]).set_z_index(-1)
        kernel_zone = RoundedRectangle(corner_radius=0.16, width=13.0, height=4.1)
        kernel_zone.set_fill(opacity=0).set_stroke(KERNEL, width=1.4, opacity=0.5)
        kernel_zone.move_to([0, -1.0, 0]).set_z_index(-1)
        levels = boundary(1.15, above="процесс пользователя", below="ядро Linux",
                          x0=-6.3, x1=6.3, size=16)

        code = CodePanel(['int fd = open("/dev/ttyS0", O_RDWR);'],
                         size=24, width=8.9).move_to([-1.65, 2.35, 0])
        result = capsule("fd = 3", USER, size=21).move_to([4.65, 2.35, 0])

        vfs = Card("VFS", ["виртуальная ФС", "поиск пути"], color=KERNEL,
                   width=2.9, size=18, row_h=0.4).move_to([-4.45, 0, 0])
        inode = Card("inode узла", ["тип c", "i_rdev = 4:64"], color=KERNEL,
                     width=3.05, size=18, row_h=0.4).move_to([-0.65, 0, 0])
        tty = Card("подсистема TTY",
                   [".open → tty_open", ".read_iter → tty_read"],
                   color=DRIVER, width=3.7, size=16, row_h=0.42)
        tty.move_to([4.15, 0, 0])

        table = Cells(4, w=1.55, h=0.42, index=range(4))
        table.shift(np.array([-4.75, -1.9, 0]) - table.cells.get_center())
        table.add(*[table.put(i, name, MUTED, 16) for i, name in
                    enumerate(("stdin", "stdout", "stderr"))])
        table.add(txt("таблица дескрипторов процесса", 16, MUTED)
                  .next_to(table.cells, UP, buff=0.08))
        opened = Card("struct file", [[("f_op → ", MUTED), ("tty_fops", DRIVER)]],
                      color=KERNEL, width=3.35, size=19, row_h=0.48)
        opened.move_to([0, -1.85, 0])
        slot = table.put(3, "file", USER, 18)

        to_vfs = poly_arrow(code.frame.get_bottom() + DOWN * 0.07,
                            vfs.frame.get_top() + UP * 0.07, color=USER)
        to_inode = poly_arrow(vfs.frame.get_right(), inode.frame.get_left(), color=KERNEL)
        to_tty = poly_arrow(inode.frame.get_right(), tty.frame.get_left(), color=DRIVER)
        table_link = poly_arrow(table.cells[3].get_right(), opened.frame.get_left(),
                                color=USER)
        ops_link = poly_arrow(opened.frame.get_right(),
                              [tty.frame.get_x(), tty.frame.get_bottom()[1], 0],
                              color=DRIVER)

        self.play(FadeIn(user_zone), FadeIn(kernel_zone), FadeIn(levels),
                  FadeIn(code), run_time=0.8)
        self.say("`open()` передаёт путь `/dev/ttyS0` в ядро",
                 FadeIn(vfs), grow(to_vfs), run_time=0.9)

        self.say("VFS разрешает путь и находит inode узла",
                 FadeIn(inode), grow(to_inode), run_time=0.9)
        self.say("Номер `4:64` приводит к обработчикам TTY",
                 FadeIn(tty), grow(to_tty), flash(inode.rows[1], YELLOW),
                 run_time=0.9)

        self.say("`struct file` хранит операции открытого устройства",
                 FadeIn(opened), grow(ops_link), run_time=0.9)
        self.play(FadeIn(table), run_time=0.5)
        self.say("Таблица процесса ссылается на `struct file`",
                 FadeIn(slot), grow(table_link), flash(table.cells[3], USER),
                 run_time=0.9)
        self.say("*fd = 3* – индекс этой таблицы, не адрес",
                 FadeIn(result), flash(table.cells[3], USER), run_time=0.9)
        self.pause(0.9)
        self.clear_all()
