# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2023 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from typing import Callable

import pygame_menu
from pygame_menu import locals
from pygame_menu.baseimage import POSITION_CENTER

from tuxemon import formula, prepare, tools
from tuxemon.db import OutputBattle, SeenStatus, db
from tuxemon.locale import T
from tuxemon.menu.menu import BACKGROUND_COLOR, PygameMenuState
from tuxemon.menu.theme import get_theme
from tuxemon.session import local_session

MenuGameObj = Callable[[], object]


def fix_width(screen_x: int, pos_x: float) -> int:
    """it returns the correct width based on percentage"""
    value = round(screen_x * pos_x)
    return value


def fix_height(screen_y: int, pos_y: float) -> int:
    """it returns the correct height based on percentage"""
    value = round(screen_y * pos_y)
    return value


class PlayerState(PygameMenuState):
    """Menu for the Journal Info state.

    Shows details of the single monster."""

    def add_menu_items(
        self,
        menu: pygame_menu.Menu,
    ) -> None:
        width = menu._width
        height = menu._height

        player = local_session.player

        if player.name == "":
            name = T.translate(player.slug).upper()
        else:
            name = player.name.upper()

        # tuxepedia data
        monsters = list(db.database["monster"])
        filters = []
        for mon in monsters:
            results = db.lookup(mon, table="monster")
            if results.txmn_id > 0:
                filters.append(results)
        tuxepedia = list(player.tuxepedia.values())
        caught = tuxepedia.count(SeenStatus.caught)
        seen = tuxepedia.count(SeenStatus.seen) + caught
        percentage = formula.sync(player, seen, len(filters))

        msg_progress = T.format(
            "tuxepedia_progress", {"value": str(percentage)}
        )
        msg_seen = T.format(
            "tuxepedia_data_seen",
            {"param": str(seen), "all": str(len(filters))},
        )
        msg_caught = T.format(
            "tuxepedia_data_caught",
            {"param": str(caught), "all": str(len(filters))},
        )
        date_begin = formula.today_ordinal() - int(
            player.game_variables["date_start_game"]
        )
        msg_begin = T.format(
            "player_start_adventure",
            {"date": str(date_begin)},
        )
        tot = len(player.battles)
        won = sum(
            1
            for battle in player.battles
            if battle.outcome == OutputBattle.won
        )
        draw = sum(
            1
            for battle in player.battles
            if battle.outcome == OutputBattle.draw
        )
        lost = sum(
            1
            for battle in player.battles
            if battle.outcome == OutputBattle.lost
        )
        msg_battles = T.format(
            "player_battles",
            {
                "tot": str(tot),
                "won": str(won),
                "draw": str(draw),
                "lost": str(lost),
            },
        )
        # steps
        steps = player.game_variables["steps"]
        if prepare.CONFIG.unit == "metric":
            walked = formula.convert_km(steps)
            unit_walked = "km"
        else:
            walked = formula.convert_mi(steps)
            unit_walked = "mi"
        msg_walked = T.format(
            "player_walked",
            {
                "distance": str(walked),
                "unit": unit_walked,
            },
        )
        # name
        menu._auto_centering = False
        menu.add.label(
            title=name,
            label_id="name",
            font_size=30,
            align=locals.ALIGN_LEFT,
            underline=True,
            float=True,
        ).translate(fix_width(width, 0.45), fix_height(height, 0.15))
        # money
        money = player.money["player"]
        menu.add.label(
            title=T.translate("wallet") + ": " + str(money),
            label_id="money",
            font_size=15,
            align=locals.ALIGN_LEFT,
            float=True,
        ).translate(fix_width(width, 0.45), fix_height(height, 0.25))
        # seen
        menu.add.label(
            title=msg_seen,
            label_id="seen",
            font_size=15,
            align=locals.ALIGN_LEFT,
            float=True,
        ).translate(fix_width(width, 0.45), fix_height(height, 0.30))
        # caught
        menu.add.label(
            title=msg_caught,
            label_id="caught",
            font_size=15,
            align=locals.ALIGN_LEFT,
            float=True,
        ).translate(fix_width(width, 0.45), fix_height(height, 0.35))
        # begin adventure
        menu.add.label(
            title=msg_begin,
            label_id="begin",
            font_size=15,
            align=locals.ALIGN_LEFT,
            float=True,
        ).translate(fix_width(width, 0.45), fix_height(height, 0.40))
        # walked
        menu.add.label(
            title=msg_walked,
            label_id="walked",
            font_size=15,
            align=locals.ALIGN_LEFT,
            float=True,
        ).translate(fix_width(width, 0.45), fix_height(height, 0.45))
        # battles
        menu.add.label(
            title=msg_battles,
            label_id="battle",
            font_size=15,
            align=locals.ALIGN_LEFT,
            float=True,
        ).translate(fix_width(width, 0.45), fix_height(height, 0.50))
        # % tuxepedia
        menu.add.label(
            title=msg_progress,
            label_id="progress",
            font_size=15,
            align=locals.ALIGN_LEFT,
            float=True,
        ).translate(fix_width(width, 0.45), fix_height(height, 0.10))
        # image
        combat_front = ""
        for ele in player.template:
            combat_front = ele.combat_front
        new_image = pygame_menu.BaseImage(
            tools.transform_resource_filename(
                "gfx/sprites/player/" + combat_front + ".png"
            ),
        )
        new_image.scale(prepare.SCALE, prepare.SCALE)
        image_widget = menu.add.image(image_path=new_image.copy())
        image_widget.set_float(origin_position=True)
        image_widget.translate(
            fix_width(width, 0.17), fix_height(height, 0.08)
        )

    def __init__(self) -> None:
        width, height = prepare.SCREEN_SIZE

        background = pygame_menu.BaseImage(
            image_path=tools.transform_resource_filename(
                "gfx/ui/item/player_info.png"
            ),
            drawing_position=POSITION_CENTER,
        )
        theme = get_theme()
        theme.scrollarea_position = locals.POSITION_EAST
        theme.background_color = background
        theme.widget_alignment = locals.ALIGN_CENTER

        super().__init__(height=height, width=width)

        self.add_menu_items(self.menu)
        self.repristinate()

    def repristinate(self) -> None:
        """Repristinate original theme (color, alignment, etc.)"""
        theme = get_theme()
        theme.scrollarea_position = locals.SCROLLAREA_POSITION_NONE
        theme.background_color = BACKGROUND_COLOR
        theme.widget_alignment = locals.ALIGN_LEFT
