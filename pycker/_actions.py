import logging
import re
import random
import time
from collections import deque
from dateutil.relativedelta import relativedelta as du_relativedelta
import datetime

from _util import coroutine, extract_region, extract_text, update_ui_element
from _skill_combo import SkillCombo

_LOG = logging.getLogger(__name__)


# @coroutine
# def update_ui_elements():
#     while True:
#         session = yield
#         game = session.game
#         turn = session.turn
#
#         elements = [e for e in game.iter_ui_elements() if e.last_update < turn.time]
#         elements = deque(elements)
#         sorted_elements = []
#         while elements:
#             element = elements.popleft()
#             try:
#                 parent = game.ui_elements[element.parent]
#             except KeyError:
#                 parent = None
#             else:
#                 if parent in elements:
#                     elements.append(element)
#
#
#                 try:
#                     parent_idx = sorted_elements.index(parent)
#                 except ValueError:
#                     if parent in elements:
#                         elements.append(element)
#                         continue
#                 else:
#                     elements.append(element)
#
#             else:
#                 order.insert(parent_idx+1, element)
#
#             if element.last_update >= session.turn.time:
#                 continue
#             if element is root_element or not element.is_static:
#                 continue
#             update_ui_element(element, root_element)


# @coroutine
# def initialize_state():
#     initialized = False
#     raid_reset_expr = r'.*?(?P<hours>[0-9]*?)\:?(?P<minutes>[0-9]*)\:(?P<seconds>[0-9]*)$'
#     raid_reset_expr = re.compile(raid_reset_expr)
#
#     while True:
#         session = yield
#         game = session.game
#
#         if initialized:
#             continue
#
#         initialized = True
#
#         root = game.ui_elements['root']
#         session.click(*game.ui_elements['tab_clan'].click_position,
#                       duration=1.0)
#         session.click(*game.ui_elements['button_current_raid'].click_position,
#                       duration=1.0)
#
#         time.sleep(1.0)
#
#         element = game.ui_elements['label_raid_reset']
#         update_ui_element(element, root)
#         raid_reset = extract_text(element.region_pil)
#         raid_reset = raid_reset_expr.match(raid_reset)
#         raid_reset = (
#             int(raid_reset.group('hours') or 0.0),
#             int(raid_reset.group('minutes') or 0.0),
#             int(raid_reset.group('seconds') or 0.0)
#         )
#         raid_reset = du_relativedelta(hours=+raid_reset[0],
#                                       minutes=+raid_reset[1],
#                                       seconds=+raid_reset[2])
#         raid_reset = datetime.datetime.now() + raid_reset
#         session.raid_reset = raid_reset


@coroutine
def update_current_zone():
    while True:
        session = yield

        if not session.active:
            continue

        zone_text = session.extract_ui_element_text('label_current_zone')
        zone_text = zone_text.strip().replace(' ', '')
        try:
            zone = int(re.match(r'\D*(\d*)$', zone_text).group(1))
        except (AttributeError, ValueError):
            continue
        if zone > session.current_zone:
            session.current_zone = zone


@coroutine
def idle():
    auto_idle = False
    auto_idle_end = 0

    while True:
        session = yield

        turn = session.turn

        if session.active:
            if not (session.current_zone - 1) % 100:
                msg = 'Engaging Auto Idle - 30s'
                _LOG.info(msg)

                auto_idle = True
                auto_idle_end = turn.time + du_relativedelta(seconds=+30)
                session.active = False
        else:
            session.click_ui_element('region_monster_attack', duration=0.01)

            if auto_idle and turn.time >= auto_idle_end:
                msg = 'Disengaging Auto Idle'
                _LOG.info(msg)

                auto_idle = False
                session.active = True


@coroutine
def accept_discovered_relic():
    while True:
        session = yield

        if not session.active:
            continue

        element = session.update_ui_element('label_relic_discovered')
        if not element.click_position:
            continue

        msg = 'Claiming Relic'
        _LOG.info(msg)
        session.click_ui_element('button_accept_relic', duration=2.0)

        msg = 'Closing Relic Discovery Window'
        _LOG.info(msg)
        session.click_ui_element('button_close_relic_window')

        msg = 'Salvaging Relics'
        _LOG.info(msg)
        session.click_ui_element('tab_relics', duration=0.5)
        session.click_ui_element('button_salvage_relics', duration=0.5)
        session.click_ui_element('button_salvage_relics_confirm', duration=0.5)

        msg = 'Navigating to Hero Tab'
        _LOG.info(msg)
        session.click_ui_element('tab_heroes', duration=1.0)


@coroutine
def activate_clickables():
    while True:
        session = yield

        if not session.active:
            continue

        game = session.game
        clickables = [session.skill_clickable]

        if session.current_zone < session.optimal_zone - 500:
            clickables.append(session.ruby_clickable)

        for clickable in clickables:
            element_name = game.clickables[clickable].ui_element

            try:
                session.click_ui_element(element_name)
            except TypeError:
                msg = 'Skipped clickable: "{0}" - No click position data'
                msg = msg.format(clickable)
            else:
                msg = 'Activated clickable: "{0}"'
                msg = msg.format(clickable)
            finally:
                _LOG.debug(msg)


@coroutine
def activate_skills():
    combos = []

    combo = SkillCombo()
    combo.skills = [
        'energize',
        'the_dark_ritual',
        'reload'
    ]
    combo.conditions = [
        lambda _session: _session.game.heroes["Grant, The General"].current_level
    ]
    combo.primary_skill = 'the_dark_ritual'
    combos.append(combo)

    combo = SkillCombo()
    combo.skills = [
        'clickstorm',
        'powersurge',
        'lucky_strikes',
        'metal_detector',
        'golden_clicks',
        'super_clicks'
    ]
    combo.conditions = [
        lambda _session: _session.game.heroes["Aphrodite, Goddess of Love"].current_level
    ]
    combo.primary_skill = 'clickstorm'
    combos.append(combo)

    while True:
        session = yield

        if not session.active:
            continue

        for combo in combos:
            skills = [session.game.skills[skill] for skill in combo.skills]

            try:
                primary_skill = session.game.skills[combo.primary_skill]
            except KeyError:
                primary_skill = None

            if primary_skill:
                if primary_skill.cooled_down > session.turn.time:
                    continue
            elif any([s.cooled_down > session.turn.time for s in skills]):
                continue

            if not all([c(session) for c in combo.conditions]):
                continue

            for i, skill in enumerate(skills):
                cooldown = skill.base_cooldown
                if combo.skills[i-1] == 'reload':
                    cooldown = int(cooldown * 0.5)

                session.click_ui_element(skill.ui_element, duration=0.01)
                _LOG.debug('activated skill: {0}'.format(skill))

                cooldown = du_relativedelta(seconds=+cooldown)
                skill.cooled_down = datetime.datetime.now() + cooldown


@coroutine
def update_hero():
    while True:
        session = yield

        if not session.active:
            continue

        game = session.game
        for hero in game.iter_heroes():
            if hero.maximum_level and hero.current_level >= hero.maximum_level:
                continue
            session.hero = hero.name
            break
        hero = game.heroes[session.hero]

        msg = 'Updating Hero Visibility "{0}"'
        msg = msg.format(hero.name)
        _LOG.debug(msg)

        root_element = session.update_ui_element('root')
        name_element = session.update_ui_element(hero.element_name)

        try:
            hero.visible = name_element.region_rect[3] + 75 <= root_element.region_rect[3]
        except TypeError:
            hero.visible = False

        if not hero.visible:
            msg = 'Hero is not visible'
            _LOG.debug(msg)
            continue

        # Update Lvl Up button
        session.update_ui_element(hero.element_level_up)

        # Compute current level
        msg = 'Computing current level "{0}"'
        msg = msg.format(hero.name)
        _LOG.debug(msg)

        level_data = session.extract_ui_element_text(hero.element_current_level)
        level_data = re.match('.*?(?P<level>[0-9]+).*?', level_data)
        try:
            level = int(level_data.group('level'))
        except (AttributeError, ValueError):
            msg = 'Computing current level "{0}"'
            msg = msg.format(hero.name)
        else:
            if level > hero.current_level:
                msg = 'Level changed: {0} -> {1}'
                msg = msg.format(hero.current_level, level)

                hero.current_level = level
            else:
                msg = 'Level unchanged: {0}, ignored {1}'
                msg = msg.format(hero.current_level, level)
        finally:
            _LOG.debug(msg)

        # Compute Ability locations
        msg = 'Computing ability locations "{0}"'
        msg = msg.format(hero.name)
        _LOG.debug(msg)

        abilities_element = session.update_ui_element(hero.element_abilities)
        ability_positions = []
        ability_width = int(float(abilities_element.size[0]) / 7.0)

        for i in xrange(hero.num_abilities):
            x = abilities_element.region_rect[0]
            x += i*ability_width
            x += random.randint(5, ability_width-3)
            y = random.randint(abilities_element.region_rect[1]+2,
                               abilities_element.region_rect[3]-2)
            ability_positions.append((x, y))

        hero.ability_positions = ability_positions


@coroutine
def seek_hero():
    seek_cap = 100
    seek_count = 0
    seek_target = None
    found = 0
    num_scroll_clicks = 1

    while True:
        session = yield

        if not session.active:
            continue

        game = session.game
        hero = game.heroes[session.hero]

        if seek_target != hero.name:
            seek_target = hero.name
            found = 0

        if hero.visible:
            seek_count = 0
            found = found + 1 if found < 5 else 5
            continue
        elif bool(found):
            found = found - 1 if found > 0 else 0
            continue

        msg = 'seeking hero: "{0}"'
        msg = msg.format(hero.name)
        _LOG.debug(msg)

        scroll_element = 'up' if seek_count > (seek_cap/2) else 'down'
        scroll_element = 'button_scroll_{}'.format(scroll_element)

        for _ in xrange(num_scroll_clicks):
            session.click_ui_element(scroll_element)
            seek_count = seek_count % seek_cap + 1


@coroutine
def level_hero():
    while True:
        session = yield

        if not session.active:
            continue

        game = session.game
        keyboard = session.keyboard
        hero = game.heroes[session.hero]

        if not hero.visible:
            continue

        if hero.maximum_level is None:
            msg = 'leveling "{0}": {1} +MAX'
            mod = 'q'
        elif hero.current_level + 100 <= hero.maximum_level:
            msg = 'leveling "{0}": {1} +100'
            mod = keyboard.control_key
        elif hero.current_level + 10 <= hero.maximum_level:
            msg = 'leveling "{0}": {1} +10'
            mod = keyboard.shift_key
        elif hero.current_level + 1 <= hero.maximum_level:
            msg = 'leveling "{0}": {1} +1'
            mod = None
        else:
            continue

        msg = msg.format(hero.name, hero.current_level)
        _LOG.debug(msg)
        session.click_ui_element(hero.element_level_up, mod=mod)

        if hero.current_level <= 200:
            msg = 'purchasing abilities "{0}"'
            msg = msg.format(hero.name)
            _LOG.debug(msg)

            for pos in hero.ability_positions:
                session.click(*pos, duration=0.25)


@coroutine
def attack_monster():
    while True:
        session = yield

        if not session.active:
            continue

        game = session.game
        hero = game.heroes.get(session.hero, None)

        aps = session.attacks_per_second
        clk_duration = 1.0/session.attacks_per_second
        if hero and hero.maximum_level and hero.current_level <= 200:
            clk_count = 1
        else:
            clk_count = aps * 5

        for _ in xrange(clk_count):
            session.click_ui_element('region_monster_attack', duration=clk_duration)


# @coroutine
# def update_immortal():
#     raid_reset_expr = (
#         r'.*?(?P<hours>[0-9]*?)\:?(?P<minutes>[0-9]*)\:(?P<seconds>[0-9]*)$'
#     )
#     raid_reset_expr = re.compile(raid_reset_expr)
#     last_update = datetime.datetime.fromtimestamp(0)
#
#     while True:
#         session = yield
#         game = session.game
#
#         if not session.active:
#             continue
#         elif datetime.datetime.now() - last_update > datetime.time(1, 0, 0):
#             continue
#
#         root = game.ui_elements['root']
#         session.click(*game.ui_elements['tab_clan'].click_position,
#                       duration=1.0)
#         session.click(*game.ui_elements['button_current_raid'].click_position,
#                       duration=2.0)
#
#         # Update raid reset time
#         element = game.ui_elements['label_raid_reset']
#         update_ui_element(element, root)
#         raid_reset = extract_text(element.region_pil)
#         raid_reset = raid_reset_expr.match(raid_reset)
#         raid_reset = (
#             int(raid_reset.group('hours') or 0.0),
#             int(raid_reset.group('minutes') or 0.0),
#             int(raid_reset.group('seconds') or 0.0)
#         )
#         raid_reset = du_relativedelta(hours=+raid_reset[0],
#                                       minutes=+raid_reset[1],
#                                       seconds=+raid_reset[2])
#         session.raid_reset = datetime.datetime.now() + raid_reset
#
#         # Update next immortal turn
#         element = game.ui_elements['button_fight_immortal']
#         update_ui_element(element, root)
#         if element.click_position:
#             session.immortal_turn_reset = datetime.datetime.now()
#
#         else:
#             session.next_immortal = session.raid_reset
#             msg = 'Immortal Unavailable'
#             _LOG.info(msg)
#
#         last_update = datetime.time(1, 0, 0)


@coroutine
def attack_immortal():
    while True:
        session = yield

        if not session.immortal_ready:
            continue

        turn = session.turn

        session.click_ui_element('tab_clan', duration=1.0)
        session.click_ui_element('button_current_raid', duration=1.0)

        session.update_ui_element('panel_current_raid')

        try:
            session.click_ui_element('button_fight_immortal')
        except TypeError:
            msg = 'Immortal Unavailable'
            _LOG.info(msg)
        else:
            msg = 'Beginning Immortal Fight'
            _LOG.info(msg)

            clk_duration = 1.0/session.attacks_per_second
            end = datetime.datetime.now() + du_relativedelta(seconds=+30)
            while datetime.datetime.now() < end:
                session.click_ui_element('region_monster_attack',
                                         duration=clk_duration)

            msg = 'Finished Immortal Fight'
            _LOG.info(msg)

            # Wait for game to catch up
            time.sleep(10)

        session.next_immortal_attempt = turn.time + du_relativedelta(hours=+1)
        session.click_ui_element('tab_heroes', duration=1.0)


@coroutine
def ascend():
    while True:
        session = yield

        if not session.ascension_ready:
            continue

        session.click_ui_element('button_ascension', duration=1.0)
        session.click_ui_element('button_ascension_confirm', duration=1.0)
        session.click_ui_element('button_progression', duration=1.0)

        for hero in session.game.iter_heroes():
            hero.current_level = 0

        for skill in session.game.iter_skills():
            skill.cooled_down = datetime.datetime.now()

        session.current_zone = 0
        session.last_ascension = datetime.datetime.now()
