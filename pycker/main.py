import sys
import logging
import cProfile

from _session import Session

import _actions as actions


_LOG = logging.getLogger(__name__)
_LOG.setLevel(logging.DEBUG)


def _main():
    sh = logging.StreamHandler(sys.stdout)
    _LOG.addHandler(sh)

    tick_frequency = 0.001
    duration = 30
    optimal_level = 1400
    ruby_clickable = 'candy_cane'
    skill_clickable = 'bumble_bee'

    session = Session(tick_frequency=tick_frequency,
                      duration=duration,
                      optimal_level=optimal_level,
                      ruby_clickable=ruby_clickable,
                      skill_clickable=skill_clickable)

    action = actions.capture()
    session.actions.append(action)

    # Static Elements
    action = actions.analyze_current_level()
    session.actions.append(action)

    action = actions.analyze_current_enemy()
    session.actions.append(action)

    action = actions.analyze_ui_elements()
    session.actions.append(action)

    # Clickables
    action = actions.analyze_clickables()
    session.actions.append(action)

    action = actions.activate_clickables()
    session.actions.append(action)

    # Heroes
    action = actions.analyze_heroes()
    session.actions.append(action)

    action = actions.level_heroes()
    session.actions.append(action)

    # Skills
    action = actions.analyze_skills()
    session.actions.append(action)

    action = actions.activate_skills()
    session.actions.append(action)

    # Attacking
    attack_interval = 1.0/35.0  # 35 clicks per second
    num_attacks = 50  # 50 clicks
    action = actions.attack(attack_interval, num_attacks)
    session.actions.append(action)

    # Ascension
    # action = actions.ascend()
    # session.actions.append(action)

    # profile = cProfile.Profile()
    # profile.enable()
    session.start()
    # profile.disable()
    # profile.print_stats()


if __name__ == '__main__':
    _main()
