###         TO DO BLOCK BECAUSE I AM FORGETFUL
#MAKE SURE ZEALOTS ARENT QUEUED 
#PYLONS ARENT BEING BUILT
#CHRONOBOOST GATEWAYS (PREFERABLY THE ONES THAT JUST STARTED MAKING ZEALOTS)
#ATTACK MOVE
###


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
    async def on_start(self):
        #splits workers
        self.worker_split()
        await self.chat_send(random.choice(self.start_message()))

        nexus = self.townhalls[0]
        tp = sc2.position.Point2((135, 95))
        bp = sc2.position.Point2((40, 75))
        d1 = nexus.distance_to(tp)
        d2 = nexus.distance_to(bp)
        if (d1 > d2):
            self.proxyvar = tp
        else:
            self.proxyvar = bp

    #on_step is essentially each frame of the game
    async def on_step(self, iteration):
        #send a random probe on the start of the game to the other side of the map
        if iteration == 0:
            worker = self.workers.random
            self.scoutworker = worker
            worker.move(self.proxyvar)

        #we only have 1 nexus cuz we so cheesy - so we can access the array by the 0th element
        nexus = self.townhalls[0]
        if self.supply_workers > 13 and self.supply_workers <= 15 and not self.already_pending(UnitTypeId.PYLON):
            if self.can_afford(UnitTypeId.PYLON):
                self.scoutworker.build(UnitTypeId.PYLON, self.proxyvar)

        #build up to 4 proxy gateways
        elif self.structures(UnitTypeId.GATEWAY).amount < 4 and self.can_afford(UnitTypeId.GATEWAY):
            gate_pos = await self.find_placement(UnitTypeId.GATEWAY, near=self.proxyvar, placement_step=1)
            if gate_pos:
                self.scoutworker.build(UnitTypeId.GATEWAY,gate_pos, queue=True)
            else:
                gate_pos = await self.find_placement(UnitTypeId.GATEWAY, near=self.proxyvar, placement_step=2)
                if gate_pos:
                    self.scoutworker.build(UnitTypeId.GATEWAY,gate_pos, queue=True)

        
        #build pylons when needed
        elif not self.already_pending(UnitTypeId.PYLON) and self.supply_left <= 3:
            if self.can_afford(UnitTypeId.PYLON):
                map_center = self.game_info.map_center
                position_towards_map_center = self.start_location.towards(map_center, distance=5)
                placement_position = await self.find_placement(UnitTypeId.SPAWNINGPOOL, near=position_towards_map_center, placement_step=1)
                if placement_position:
                    worker = self.workers.random
                    worker.build(UnitTypeId.PYLON, placement_position)

        #mass those zealots up
        if self.structures(UnitTypeId.GATEWAY).ready:
            for gate in self.structures(UnitTypeId.GATEWAY):
                gate.build(UnitTypeId.ZEALOT)

        #copied from https://github.com/BurnySc2/python-sc2/blob/develop/examples/protoss/cannon_rush.py
        if self.supply_workers < 17 and nexus.is_idle:
            if self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)

    #chooses a random start message
    def start_message(self):
        return ["(glhf)", "(poo)(poo)(poo)", "glhf (happy)", "glhf (hearts)", "gtfo noob",
              "gl youre gonna need it"] 

    #splits workers - can be improved in the future
    def worker_split(self):
        for w in self.workers:
            w.gather(self.mineral_field.closest_to(w))