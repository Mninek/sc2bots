import sc2
from sc2.data import Result
from sc2.constants import *
from sc2.unit import Unit
from sc2.units import Units
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId

import random
import asyncio

class GruyereBot(sc2.BotAI):
    