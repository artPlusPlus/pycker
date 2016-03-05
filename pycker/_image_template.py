import logging
import operator
import math

import numpy
import cv2
from PIL import Image, ImageChops

from _util import extract_region

_LOG = logging.getLogger(__name__)


class ImageTemplate(object):
    _METHOD = cv2.TM_CCOEFF_NORMED

    @property
    def match_threshold(self):
        return self._match_threshold

    @property
    def cv2(self):
        return self._cv2_img

    @property
    def pil(self):
        return self._pil_img

    def __init__(self, source_filepath, match_threshold=None):
        self._filepath = source_filepath
        self._match_threshold = match_threshold
        self._pil_img = Image.open(source_filepath)
        self._cv2_img = numpy.array(self._pil_img)
        self._cv2_img = cv2.cvtColor(self._cv2_img, cv2.COLOR_RGB2GRAY)
        self._cv2_img = cv2.adaptiveThreshold(
            self._cv2_img, 230, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2)
        self._w, self._h = self._cv2_img.shape[::-1]
        # self._cv2_img = cv2.cvtColor(self._cv2_img, cv2.COLOR_RGB2BGR)
        # _, self._w, self._h = self._cv2_img.shape[::-1]

    def compute_region(self, source_pil):
        # source_cv2 = cv2.cvtColor(numpy.array(source_pil), cv2.COLOR_RGB2BGR)
        source_cv2 = cv2.cvtColor(numpy.array(source_pil), cv2.COLOR_RGB2GRAY)
        # source_cv2 = cv2.medianBlur(source_cv2, 5)
        source_cv2 = cv2.adaptiveThreshold(
                source_cv2, 230, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
                11, 2)
        match = cv2.matchTemplate(source_cv2, self._cv2_img, self._METHOD)
        if self._METHOD in (cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED):
            _, max_val, top_left, _ = cv2.minMaxLoc(match)
        else:
            _, max_val, _, top_left = cv2.minMaxLoc(match)
        result = (top_left[0],
                  top_left[1],
                  top_left[0] + self._w,
                  top_left[1] + self._h)

        if self._match_threshold:
            # source = extract_region(source_pil_img, result).convert('L')
            # target = self._pil_img.convert('L')

            source = self._pil_img
            target = extract_region(source_pil, result).convert(source.mode)

            delta = ImageChops.difference(source, target).convert('RGB')
            delta = delta.histogram()
            delta = [delta[i] + delta[i+256] + delta[i+256*2] for i in xrange(1, len(delta)/3)]
            delta = [delta[i]*(i**2) for i in xrange(len(delta))]
            delta = math.sqrt(sum(delta) / float(len(delta)))

            if delta > self._match_threshold or max_val < 0.4:
                msg = 'Image delta above threshold: {0} > {1}'
                msg = msg.format(delta, self._match_threshold)
                _LOG.debug(msg)
                return None

        return result
