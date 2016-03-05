import random
import datetime

import numpy
import cv2


class UIElement(object):
    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def template(self):
        return self._template

    @property
    def region_hint(self):
        return self._region_hint

    @property
    def region_offset_target(self):
        return self._region_offset_target

    @property
    def region_offset(self):
        return self._region_offset

    @property
    def region_rect(self):
        return self._region_rect

    @region_rect.setter
    def region_rect(self, value):
        try:
            width = value[2] - value[0]
            height = value[3] - value[1]

            click_pos = (random.randint(value[0], value[2]),
                         random.randint(value[1], value[3]))
        except TypeError:
            width = None
            height = None
            click_pos = None

        self._region_rect = value
        self._size = width, height
        self._click_position = click_pos

    @property
    def region_pil(self):
        return self._region_pil

    @region_pil.setter
    def region_pil(self, value):
        self._region_pil = value
        self._region_cv2 = None

    @property
    def region_cv2(self):
        if self._region_pil and self._region_cv2 is None:
            region_cv2 = numpy.array(self._region_pil)
            region_cv2 = cv2.cvtColor(region_cv2, cv2.COLOR_RGB2BGR)
            self._region_cv2 = region_cv2
        return self._region_cv2

    @property
    def size(self):
        return self._size

    @property
    def click_position(self):
        return self._click_position

    @property
    def is_static(self):
        return self._is_static

    @property
    def last_updated(self):
        return self._last_updated

    @last_updated.setter
    def last_updated(self, value):
        self._last_updated = value

    def __init__(self, name, parent=None, template=None, is_static=True,
                 region_hint=None, region_offset_target=None,
                 region_offset=None):
        self._name = name
        self._parent = parent
        self._template = template
        self._region_hint = region_hint
        self._region_offset_target = region_offset_target
        self._region_offset = region_offset
        self._is_static = is_static
        self._last_updated = datetime.datetime.fromtimestamp(0)

        self._region_rect = None
        self._region_pil = None
        self._region_cv2 = None
        self._size = None
        self._click_position = None
