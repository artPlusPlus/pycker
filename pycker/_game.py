import os
import logging

import win32gui

import _data
from _ui_element import UIElement
from _image_template import ImageTemplate
from _hero import Hero
from _skill import Skill
from _clickable import Clickable


_LOG = logging.getLogger(__name__)
_DEFAULT_TARGET_WINDOW = 'Clicker Heroes'


class Game(object):
    @property
    def hwnd(self):
        return win32gui.FindWindow(None, self._target_window)

    @property
    def exists(self):
        return bool(self.hwnd)

    @property
    def ui_elements(self):
        return self._ui_element_data.copy()

    @property
    def clickables(self):
        return self._clickable_data.copy()

    @property
    def skills(self):
        return self._skill_data.copy()

    @property
    def heroes(self):
        return self._hero_data.copy()

    def __init__(self, target_window=_DEFAULT_TARGET_WINDOW):
        self._target_window = target_window

        self._ui_element_data = {}
        self._ui_element_hierarchy = {}
        self._populate_ui_element_data(self._ui_element_data,
                                       self._ui_element_hierarchy)

        self._clickable_data = {}
        self._populate_clickable_data(self._clickable_data)

        self._skill_data = {}
        self._populate_skill_data(self._skill_data)

        self._hero_order = []
        self._hero_data = {}
        self._populate_hero_data(self._hero_data, self._hero_order)

    @staticmethod
    def _populate_ui_element_data(element_container, hierarchical_container):
        template_dir = os.path.dirname(__file__)
        template_dir = os.path.join(template_dir, 'static')
        for element_data in _data.UI_ELEMENT_DATA:
            name = element_data['name']
            parent = element_data.get('parent', 'root')
            static = element_data['static']
            region_hint = element_data['region_hint']
            region_offset_target = element_data.get('region_offset_target')
            region_offset = element_data.get('region_offset')
            template = element_data['template']
            template_match_threshold = element_data['template_match_threshold']

            if template:
                template = os.path.join(template_dir, template)
                template = ImageTemplate(template,
                                         match_threshold=template_match_threshold)

            element = UIElement(name, parent=parent, template=template,
                                is_static=static, region_hint=region_hint,
                                region_offset_target=region_offset_target,
                                region_offset=region_offset)
            element_container[element.name] = element
            hierarchical_container[element] = element.parent

    @staticmethod
    def _populate_clickable_data(container):
        for clickable_data in _data.CLICKABLE_DATA:
            name = clickable_data['name']
            ui_element = clickable_data['ui_element']
            clickable = Clickable(name, ui_element)
            container[clickable.name] = clickable

    @staticmethod
    def _populate_skill_data(container):
        for skill_data in _data.SKILL_DATA:
            name = skill_data['name']
            ui_element = skill_data['ui_element']
            cooldown = skill_data['cooldown']
            skill = Skill(name, ui_element, cooldown)
            container[skill.name] = skill

    @staticmethod
    def _populate_hero_data(map_container, sequence_container):
        for hero_data in _data.HERO_DATA:
            name = hero_data['name']
            maximum_level = hero_data['maximum_level']
            num_abilities = hero_data['num_abilities']
            name_element = hero_data['name_element']
            current_level_element = hero_data['current_level_element']
            level_up_element = hero_data['level_up_element']
            ability_element = hero_data['ability_element']

            hero = Hero(
                    name, maximum_level, num_abilities, name_element,
                    current_level_element, level_up_element, ability_element)
            map_container[name] = hero
            sequence_container.append(hero)

    def iter_ui_elements(self):
        for element in self._ui_element_data.itervalues():
            yield element

    def iter_skills(self):
        for skill in self._skill_data.itervalues():
            yield skill

    def iter_heroes(self):
        for hero in self._hero_order:
            yield hero
