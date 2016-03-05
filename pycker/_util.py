import random

import pytesseract
import numpy

import win32gui
import desktopmagic.screengrab_win32 as screengrab
from PIL import Image, ImageOps, ImageFilter


_TARGET_WINDOW = 'Clicker Heroes'
_TARGET_HWND = win32gui.FindWindow(None, _TARGET_WINDOW)


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        cr.next()
        return cr
    return start


def update_ui_element(element, parent, offset_target):
    element_rect = None
    element_pil = None

    if parent:
        root_rect = parent.region_rect
        root_size = parent.size
    else:
        root_rect = win32gui.GetWindowRect(_TARGET_HWND)
        root_size = (
            root_rect[2] - root_rect[0],
            root_rect[3] - root_rect[1]
        )

    if element.is_static:
        try:
            root_pil = parent.region_pil
        except AttributeError:
            root_pil = screengrab.getRectAsImage(root_rect).convert('RGB')
    else:
        root_pil = screengrab.getRectAsImage(root_rect).convert('RGB')

    source_rect = [None, None, None, None]
    if element.region_hint:
        for i, hint in enumerate(element.region_hint):
            if hint is None:
                continue
            source_rect[i] = int(root_size[i % 2] * element.region_hint[i])

    if offset_target:
        for i, offset in enumerate(element.region_offset):
            if offset is None:
                continue
            target_rect_idx, offset_value = offset
            source_rect[i] = offset_target.region_rect[target_rect_idx]
            source_rect[i] += offset_value
            source_rect[i] -= root_rect[i % 2]

    if any([d is None for d in source_rect]):
        source_pil = root_pil
    else:
        source_pil = extract_region(root_pil, source_rect)

        element_rect = source_rect
        element_pil = source_pil

    if element.template:
        try:
            template_rect = element.template.compute_region(source_pil)
        except Exception as e:
            msg = 'Failed to match ui element: {0} - {1}'
            msg = msg.format(element.name, e)
            print msg

            template_rect = None

        if not template_rect:
            element_rect = None
            element_pil = None
        elif source_pil is not root_pil:
            element_rect = (
                element_rect[0] + template_rect[0],
                element_rect[1] + template_rect[1],
                element_rect[0] + template_rect[2],
                element_rect[1] + template_rect[3],
            )
            element_pil = extract_region(source_pil, template_rect)
        else:
            element_rect = template_rect
            element_pil = extract_region(source_pil, template_rect)

    if element_rect:
        element_rect = (
            root_rect[0] + element_rect[0],
            root_rect[1] + element_rect[1],
            root_rect[0] + element_rect[2],
            root_rect[1] + element_rect[3],
        )

    element.region_rect = element_rect
    element.region_pil = element_pil


def extract_text(src_img, invert=True):
    vec = lambda px: 0 if px <= 253 else 255
    vec = numpy.vectorize(vec)

    src = src_img.convert('L')
    src = vec(numpy.array(src))
    src = Image.fromarray(src).convert('L')
    src = src.filter(ImageFilter.UnsharpMask(radius=0.5, percent=50, threshold=3))
    if invert:
        src = ImageOps.invert(src)

    result = pytesseract.image_to_string(src)

    return result


def extract_region(source_img, region_rect):
    result = source_img.copy()
    result = result.crop(box=region_rect)
    return result


def compute_ability_positions(self, hero, region_abilities):
    result = []
    ability_width = int(float(region_abilities.size[0]) / 7.0)
    for i in xrange(hero.num_abilities):
        x = region_abilities.region_rect[0]
        x += i*ability_width
        x += random.randint(5, ability_width-3)
        y = random.randint(region_abilities.region_rect[1]+2,
                           region_abilities.region_rect[3]-2)
        result.append((x, y))