import datetime


class Skill(object):
    def __init__(self, name, ui_element, base_cooldown):
        self.name = name
        self.ui_element = ui_element
        self.base_cooldown = base_cooldown
        self.cooled_down = datetime.datetime.fromtimestamp(0)
