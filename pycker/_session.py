import time
import logging
from collections import deque

import datetime
from dateutil.relativedelta import relativedelta as du_relativedelta
from pymouse import PyMouse
from pykeyboard import PyKeyboard

from _game import Game
from _turn import Turn
from _util import update_ui_element, extract_text


_LOG = logging.getLogger(__name__)


class Session(object):
    @property
    def game(self):
        return self._game

    @property
    def mouse(self):
        return self._mouse

    @property
    def keyboard(self):
        return self._keyboard

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value

    @property
    def elapsed(self):
        if self._start_time is None:
            raise RuntimeError('Not started!')
        return datetime.datetime.now() - self._start_time

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = bool(value)

    @property
    def next_idle_tick(self):
        return self._next_idle_tick

    @next_idle_tick.setter
    def next_idle_tick(self, value):
        self._next_idle_tick = value

    @property
    def turn(self):
        return self._turn

    @property
    def current_zone(self):
        return self._current_zone

    @current_zone.setter
    def current_zone(self, value):
        self._current_zone = value

    @property
    def optimal_zone(self):
        return self._optimal_zone

    @optimal_zone.setter
    def optimal_zone(self, value):
        self._optimal_zone = value

    @property
    def attacks_per_second(self):
        return self._attacks_per_second

    @property
    def ruby_clickable(self):
        return self._ruby_clickable

    @property
    def skill_clickable(self):
        return self._skill_clickable

    @property
    def hero(self):
        if self._hero_override:
            return self._hero_override
        return self._current_hero

    @hero.setter
    def hero(self, value):
        if self._hero_override:
            msg = 'Hero Override set, discarding hero value "{0}"'
            msg = msg.format(value)
            _LOG.warn(msg)
        elif value != self._current_hero:
            msg = 'Hero Changed: "{0}" -> "{1}"'
            msg = msg.format(self._current_hero, value)
            _LOG.info(msg)
            self._current_hero = value

    @property
    def next_immortal_attempt(self):
        return self._next_immortal_attempt

    @next_immortal_attempt.setter
    def next_immortal_attempt(self, value):
        self._next_immortal_attempt = value

    @property
    def immortal_ready(self):
        result = all([
            self.active,
            self._auto_raid,
            self.next_immortal_attempt < datetime.datetime.now(),
            self._current_zone >= self._optimal_zone - 5
        ])
        return result

    @property
    def time_since_ascension(self):
        return time.time() - self._last_ascension

    @property
    def last_ascension(self):
        return self._last_ascension

    @last_ascension.setter
    def last_ascension(self, value):
        self._last_ascension = value

    @property
    def auto_ascend(self):
        return self._auto_ascend

    @auto_ascend.setter
    def auto_ascend(self, value):
        self._auto_ascend = bool(value)

    @property
    def ascension_ready(self):
        result = all([
            self.active,
            self._auto_ascend,
            self._current_zone > self._optimal_zone
        ])
        return result

    @property
    def _continue(self):
        result = [
            self.game.exists,
            not self._stopped,
            not self._duration or self.elapsed < self._duration
        ]
        result = all(result)
        return result

    def __init__(self, tick_frequency=.01, duration=None,
                 ruby_clickable=None, skill_clickable=None,
                 optimal_level=None, attacks_per_second=35,
                 hero_override=None, auto_ascend=True,
                 auto_raid=True):
        super(Session, self).__init__()

        self._game = Game()
        self._mouse = PyMouse()
        self._keyboard = PyKeyboard()

        self._start_time = None
        self._stopped = False
        self._active = False
        self._next_active_tick = datetime.datetime.fromtimestamp(0)
        self._next_idle_tick = datetime.datetime.fromtimestamp(0)

        self._tick_frequency = tick_frequency
        self._duration = duration
        self._ruby_clickable = ruby_clickable
        self._skill_clickable = skill_clickable
        self._optimal_zone = optimal_level
        self._attacks_per_second = attacks_per_second
        self._hero_override = hero_override
        self._auto_ascend = auto_ascend
        self._auto_raid = auto_raid

        self._turn = None
        self._current_zone = 0
        self._current_hero = None
        self._next_immortal_attempt = datetime.datetime.fromtimestamp(0)
        self._last_ascension = 0

        self.actions = []

    def start(self):
        start_time = datetime.datetime.now()

        msg = 'Starting session: {0}'
        msg = msg.format(start_time)
        _LOG.info(msg)

        self._start_time = start_time
        self._last_ascension = self._start_time

        while self._continue:
            now = datetime.datetime.now()
            if self._active and now < self._next_active_tick:
                continue
            elif not self._active and now < self._next_idle_tick:
                continue

            with Turn(self) as turn:
                self._turn = turn
                for action in self.actions:
                    action.send(self)
            self._next_active_tick = datetime.datetime.now() + du_relativedelta(seconds=+self._tick_frequency)
            self._next_idle_tick = datetime.datetime.now() + du_relativedelta(seconds=+30)

        msg = 'Finished session: {0}'
        msg = msg.format(datetime.datetime.now())
        _LOG.info(msg)

    def update_ui_element(self, ui_element_name):
        pool = deque([ui_element_name])
        elements = []
        while pool:
            element = self.game.ui_elements[pool.popleft()]
            if element.parent:
                pool.append(element.parent)
            if element.region_offset_target:
                pool.append(element.region_offset_target)
            if element in elements:
                elements.remove(element)
            elements.insert(0, element)

        for element in elements:
            if element.last_updated >= self.turn.time:
                continue
            parent = self.game.ui_elements.get(element.parent)
            offset_target = self.game.ui_elements.get(element.region_offset_target)
            update_ui_element(element, parent, offset_target)
            element.last_updated = self.turn.time

        root = self.game.ui_elements['root']
        result = self.game.ui_elements[ui_element_name]
        if root is not result and result.region_rect:
            for i in xrange(4):
                if i < 2 and result.region_rect[i] < root.region_rect[i]:
                    result.region_rect[i] = root.region_rect[i]
                elif i > 1 and result.region_rect[i] > root.region_rect[i]:
                    result.region_rect[i] = root.region_rect[i]
            result.region_rect = tuple(result.region_rect)

        return result

    def extract_ui_element_text(self, ui_element_name):
        region_pil = self.update_ui_element(ui_element_name).region_pil
        result = extract_text(region_pil)
        return result

    def click_ui_element(self, ui_element_name, duration=0.5, mod=None):
        click_pos = self.update_ui_element(ui_element_name).click_position
        self.click(*click_pos, duration=duration, mod=mod)

    def click(self, x, y, duration=0.5, mod=None):
        if mod:
            self._keyboard.press_key(mod)
            self._mouse.click(x, y)
            self._keyboard.release_key(mod)
        else:
            self._mouse.click(x, y)
        time.sleep(duration)

    def stop(self):
        self._active = False
        self._stopped = True
