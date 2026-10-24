"""Весь ролик одной сценой: фрагменты 0–6 подряд.

FullVideo наследует все фрагменты, поэтому их construct() можно вызвать на одном
объекте сцены, и вспомогательные методы фрагментов при этом тоже доступны.
"""
from s0_title import TitleScene
from s1_dev_files import DevFilesScene
from s2_open import OpenScene
from s3_read import ReadScene
from s4_mmap import MmapScene
from s5_shared import SharedScene
from s6_framebuffer import FramebufferScene

PARTS = (TitleScene, DevFilesScene, OpenScene, ReadScene, MmapScene, SharedScene, FramebufferScene)


class FullVideo(*PARTS):
    def construct(self):
        for part in PARTS:
            part.construct(self)
