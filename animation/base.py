"""Базовая сцена: фон, заставка главы, субтитры и очистка экрана."""
from manim import *

from components import mode_badge, mono, rich, txt
from style import *


class BaseScene(Scene):
    """Общая основа всех фрагментов.

    Вспомогательные методы сцен-фрагментов определены в их классах, а FullVideo
    наследует все фрагменты сразу, поэтому имена этих методов не должны совпадать.
    """

    def setup(self):
        self.camera.background_color = BG
        self.caption = None
        self.caption_visible_at = None
        self.header = None

    def chapter(self, num, title, color=BLUE):
        """Номер и название главы крупно по центру, затем — маленькой шапкой в углу."""
        big = VGroup(mono(num, 34, color, weight=BOLD), txt(title, 40, TEXT, weight=BOLD))
        big.arrange(RIGHT, buff=0.4)
        small = VGroup(mono(num, 17, color, weight=BOLD), txt(title, 18, MUTED))
        small.arrange(RIGHT, buff=0.16).to_corner(UL, buff=0.25)
        self.play(FadeIn(big, shift=UP * 0.25), run_time=0.45)
        self.wait(0.8)
        self.play(Transform(big, small), run_time=0.5)
        self.header = big

    def pause(self, t):
        """Пауза на чтение; общий темп задаётся style.PAUSE."""
        self.wait(t * PAUSE)

    def show_mode(self):
        """Значок «режим пользователя / режим ядра» (анимация появления)."""
        self.badge = mode_badge(False)
        return FadeIn(self.badge)

    def mode(self, kernel):
        """Переключить значок без наложения двух подписей друг на друга."""
        self.remove(self.badge)
        self.badge = mode_badge(kernel)
        return FadeIn(self.badge)

    def say(self, s, *anims, accent=YELLOW, run_time=0.5):
        """Сменить субтитр внизу кадра (можно вместе с другими анимациями)."""
        self.hold_caption()
        new = rich(s, CAPTION_SIZE, TEXT, accent)
        if new.width > 13.4:
            new.scale_to_fit_width(13.4)
        new.move_to([0, CAPTION_Y, 0])
        # Одновременный FadeOut/FadeIn даёт две читаемые строки поверх друг друга.
        # Короткая смена без перекрытия лучше работает для учебного ролика.
        if self.caption is not None:
            self.remove(self.caption)
        self.play(FadeIn(new, shift=UP * 0.08), *anims, run_time=run_time)
        self.caption = new
        # Время чтения отсчитывается после окончания появления текста.
        self.caption_visible_at = self.time

    def hold_caption(self):
        """Не менять тезис, пока зритель не успел прочитать нижнюю строку."""
        if self.caption is None or self.caption_visible_at is None:
            return
        remaining = MIN_CAPTION_HOLD - (self.time - self.caption_visible_at)
        if remaining > 0:
            self.wait(remaining)

    def clear_stage(self, *keep, run_time=0.6):
        """Убрать схему, оставив шапку, субтитр, значок режима и объекты `keep`."""
        kept = {id(m) for m in (self.header, self.caption, getattr(self, "badge", None), *keep)}
        self.play(*[FadeOut(m) for m in self.mobjects if id(m) not in kept], run_time=run_time)

    def clear_all(self, run_time=0.6):
        """Плавно убрать всё с экрана (конец фрагмента)."""
        self.hold_caption()
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self.caption = None
        self.caption_visible_at = None
