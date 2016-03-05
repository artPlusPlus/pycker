import logging
import time

_LOG = logging.getLogger(__name__)


class SkillCombo(object):
    def __init__(self):
        super(SkillCombo, self).__init__()
        self.skills = []
        self.conditions = []
        self.primary_skill = None

