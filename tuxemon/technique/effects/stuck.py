# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2023 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import random
from dataclasses import dataclass

from tuxemon import formula
from tuxemon.monster import Monster
from tuxemon.technique.techeffect import TechEffect, TechEffectResult
from tuxemon.technique.technique import Technique


class StuckEffectResult(TechEffectResult):
    pass


@dataclass
class StuckEffect(TechEffect):
    """
    This effect has a chance to apply the stuck status effect.
    """

    name = "stuck"
    objective: str

    def apply(
        self, tech: Technique, user: Monster, target: Monster
    ) -> StuckEffectResult:
        player = self.session.player
        potency = random.random()
        value = float(player.game_variables["random_tech_hit"])
        obj = self.objective
        success = tech.potency >= potency and tech.accuracy >= value
        if success:
            tech = Technique("status_stuck")
            if obj == "user":
                user.apply_status(tech)
                formula.simple_stuck(user)
            elif obj == "target":
                target.apply_status(tech)
                formula.simple_stuck(target)
            return {"success": True}
        if tech.slug == "status_stuck":
            return {"success": True}

        return {"success": False}
