class Hero(object):
    @property
    def name(self):
        return self._name

    @property
    def maximum_level(self):
        return self._maximum_level

    @property
    def num_abilities(self):
        return self._num_abilities

    @property
    def element_name(self):
        return self._element_name

    @property
    def element_current_level(self):
        return self._element_current_level

    @property
    def element_level_up(self):
        return self._element_level_up

    @property
    def element_abilities(self):
        return self._element_abilities

    def __init__(self, name, maximum_level, num_abilities, name_element,
                 current_level_element, level_up_element, abilities_element):
        self._name = name
        self._maximum_level = maximum_level
        self._num_abilities = num_abilities

        self._element_name = name_element
        self._element_current_level = current_level_element
        self._element_level_up = level_up_element
        self._element_abilities = abilities_element

        self.current_level = 0
        self.visible = False
