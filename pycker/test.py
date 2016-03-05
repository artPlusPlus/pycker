import time
import logging
import datetime

from pycker._session import Session
import _actions as actions


_LOG = logging.getLogger(__name__)


def _test_current_zone():
    tick_frequency = 1

    session = Session(tick_frequency=tick_frequency, duration=1.5)
    session.active = True

    action = actions.update_static_ui_elements()
    session.actions.append(action)

    action = actions.update_current_zone()
    session.actions.append(action)

    session.start()

    print session.current_zone


def _test_hero_visibility(hero_name):
    duration = datetime.timedelta(seconds=1, milliseconds=500)
    session = Session(tick_frequency=1, duration=duration,
                      hero_override=hero_name)
    session.active = True

    # action = actions.update_static_ui_elements()
    # session.actions.append(action)

    action = actions.update_hero()
    session.actions.append(action)

    session.start()

    game = session.game
    hero = game.heroes[session.hero]

    element = game.ui_elements[hero.element_name]

    print hero.visible

    try:
        element.region_pil.show()
    except (TypeError, AttributeError):
        print 'NO NAME REGION'


def _test_hero_level(hero_name):
    duration = datetime.timedelta(seconds=1)
    session = Session(tick_frequency=1, duration=duration,
                      hero_override=hero_name)
    session.active = True

    action = actions.update_hero()
    session.actions.append(action)

    session.start()

    hero = session.game.heroes[hero_name]
    element = session.game.ui_elements[hero.element_current_level]

    try:
        element.region_pil.show()
    except AttributeError:
        print 'NO REGION MATCH'

    print hero.current_level


def _test_hero_level_up_region(hero_name):
    duration = datetime.timedelta(seconds=1, milliseconds=500)
    session = Session(tick_frequency=1, duration=duration,
                      hero_override=hero_name)
    session.active = True

    action = actions.update_hero()
    session.actions.append(action)

    session.start()

    game = session.game
    hero = game.heroes[session.hero]

    element = game.ui_elements[hero.element_level_up]

    print hero.visible

    try:
        element.region_pil.show()
        session.mouse.move(*element.click_position)
    except (TypeError, AttributeError):
        print 'NO NAME REGION'


def _test_hero_ability_region(hero_name):
    duration = datetime.timedelta(seconds=1, milliseconds=500)
    session = Session(tick_frequency=1, duration=duration,
                      hero_override=hero_name)
    session.active = True

    action = actions.update_hero()
    session.actions.append(action)

    session.start()

    game = session.game
    hero = game.heroes[session.hero]
    print hero.name

    name_element = game.ui_elements[hero.element_name]
    abilities_element = game.ui_elements[hero.element_abilities]

    try:
        # name_element.region_pil.show()
        abilities_element.region_pil.show()
        for x, y in hero.ability_positions:
            session.mouse.move(x, y)
            time.sleep(1)
    except (TypeError, AttributeError):
        print 'NO ABILITY POSITIONS'


def _test_hero_seek(hero_name):
    session = Session(tick_frequency=1, duration=20, hero_override=hero_name)
    session.active = True

    # action = actions.update_static_ui_elements()
    # session.actions.append(action)

    action = actions.update_hero()
    session.actions.append(action)

    action = actions.seek_hero()
    session.actions.append(action)

    session.start()


def _test_attack_monster():
    session = Session(tick_frequency=1, duration=1.5)
    session.active = True

    # action = actions.update_static_ui_elements()
    # session.actions.append(action)

    action = actions.attack_monster()
    session.actions.append(action)

    session.start()


def _test_attack_immortal():
    session = Session(tick_frequency=1, duration=30)
    session.active = True

    # action = actions.update_static_ui_elements()
    # session.actions.append(action)

    action = actions.attack_immortal()
    session.actions.append(action)

    session.start()


def _test_update_ui_element(element_name):
    duration = datetime.timedelta(seconds=1)
    session = Session(tick_frequency=1, duration=duration)
    session.active = True

    session.start()

    element = session.update_ui_element(element_name)
    try:
        element.region_pil.show()
        # session.mouse.move(*element.click_position)
    except (TypeError, AttributeError):
        print 'NO REGION AVAILABLE'


def _main():
    # hero = "Ivan, the Drunken Brawler"
    hero = "Cid, the Helpful Adventurer"
    # _test_hero_visibility(hero)
    # _test_hero_level(hero)
    # _test_hero_level_up_region(hero)
    # _test_hero_ability_region(hero)

    # ui_element = 'clickable_bumble_bee'
    ui_element = 'clickable_pie'
    # session.click_ui_element('button_current_raid', duration=1.0)
    # ui_element = 'button_fight_immortal'
    _test_update_ui_element(ui_element)

    # _test_static_ui_element('button_close_relic_window')
    # _test_daynamic_ui_element('label_relic_discovered')
    # _test_daynamic_ui_element('panel_heroes')
    # _test_update_ui_element('label_hero_name_orntchya')
    # _test_raid_reset()
    # _test_daynamic_ui_element('clickable_bumble_bee')
    # _test_attack_immortal()
    # _test_current_zone()
    # _test_attack_monster()

    # _test_hero_level("Treebeast")
    # _test_hero_ability_region("Cid, the Helpful Adventurer")
    # _test_hero_seek("Mercedes, Duchess of Blades")

    # _test_hero_position("Cid, the Helpful Adventurer")
    # _test_hero_level("Treebeast")
    # _test_hero_scroll_position('down')
    # _test_skill_position('ascension')

    # _test_relic_analysis()
    pass

if __name__ == '__main__':
    _main()
