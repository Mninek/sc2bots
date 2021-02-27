###         TO DO BLOCK BECAUSE I AM FORGETFUL
#   ATTACKS WORK ?? BUT ATTACK MOVE IS VERY SLOW, SPEED IT UP AND QUEUE IT SO THE ZEALOTS SLOWLY RUN UP THE RAM
#   TEST ABOVE BY SMALL CODE THAT HAS A PROBE WALK ACROSS THE MAP TO THE OPPONENTS RAMP
#
#
#
###

#idea - try to limit calls of specific units, just loop thru all and save each type somewhere


#               NOTES
#22.4 iterations per second
#
#

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

        self.start_attack = False

    #on_step is essentially each frame of the game
    async def on_step(self, iteration):
        #send a random probe on the start of the game to the other side of the map
        if iteration == 0:
            worker = self.workers.random
            self.scoutworker = worker
            worker.move(self.proxyvar)

        #we only have 1 nexus cuz we so cheesy - so we can access the array by the 0th element
        nexus = self.townhalls[0]
        if self.supply_workers > 13 and self.supply_cap <= 15 and not self.already_pending(UnitTypeId.PYLON):
            if self.can_afford(UnitTypeId.PYLON):
                self.scoutworker.build(UnitTypeId.PYLON, self.proxyvar)

        #build up to 4 proxy gateways
        elif self.structures(UnitTypeId.GATEWAY).amount < 4 and self.can_afford(UnitTypeId.GATEWAY):
            gate_pos = await self.find_placement(UnitTypeId.GATEWAY, near=self.proxyvar, placement_step=2)
            if gate_pos:
                self.scoutworker.build(UnitTypeId.GATEWAY,gate_pos, queue=True)
            else:
                gate_pos = await self.find_placement(UnitTypeId.GATEWAY, near=self.proxyvar, placement_step=3)
                if gate_pos:
                    self.scoutworker.build(UnitTypeId.GATEWAY,gate_pos, queue=True)

        #build pylons when needed
        #supply_cap > 15 means we wont build the first pylon in the base
        if not self.already_pending(UnitTypeId.PYLON) and self.supply_cap > 15 and self.supply_left <= 4:
            #start second pylon slightly earlier than normal
            if self.can_afford(UnitTypeId.PYLON):
                map_center = self.game_info.map_center
                position_towards_map_center = self.start_location.towards(map_center, distance=5)
                placement_position = await self.find_placement(UnitTypeId.PYLON, near=position_towards_map_center, placement_step=1)
                if placement_position:
                    worker = self.workers.random
                    worker.build(UnitTypeId.PYLON, placement_position)
                    worker.gather(self.mineral_field.closest_to(worker), queue=True)

        #mass those zealots up
        #or rebuild the proxy pylon if the gateways are de-powered
        if self.structures(UnitTypeId.GATEWAY).ready:
            for gate in self.structures(UnitTypeId.GATEWAY):
                if not gate.is_powered and gate.ready:
                    self.builditeration = iteration
                    if self.can_afford(UnitTypeId.PYLON):
                        if self.builditeration == iteration or self.builditeration + 336 == iteration:
                            placement_position = await self.find_placement(UnitTypeId.PYLON, near=self.proxyvar, placement_step=1)
                            if placement_position:
                                self.scoutworker.build(UnitTypeId.PYLON, placement_position)
                gate_orders = gate.orders
                if gate_orders:
                    gate_orders = gate_orders[0].progress
                else:
                    gate_orders = 0
                if (gate.is_idle or gate_orders >= .95) and self.supply_left >=2:
                    gate.build(UnitTypeId.ZEALOT)
                    if not gate.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        if nexus.energy >= 50:
                            nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, gate)

        #copied from https://github.com/BurnySc2/python-sc2/blob/develop/examples/protoss/cannon_rush.py
        if self.supply_workers < 17:
            #nexus_order = nexus.orders
            #if nexus_order:
            #    nexus_order = nexus_order[0].progress
            #else:
            #    nexus_order = 0
            #if nexus_order >= .9 or nexus.is_idle:
            if nexus.is_idle and self.can_afford(UnitTypeId.PROBE):
                nexus.train(UnitTypeId.PROBE)
        
        #begin attack when we have 4 zealots
        if self.units(UnitTypeId.ZEALOT).amount >= 4:
            self.start_attack = True

        #if we started the attack, select the zealots and have them go  
        if self.start_attack:
            for zealot in self.units(UnitTypeId.ZEALOT):
                if zealot.is_idle:
                    zealot.attack(zealot.position.towards(self.enemy_start_locations[0], 2))
                    
                    #self.enemy_start_locations[0].

    #chooses a random start message
    def start_message(self):
        return ["(glhf)", "(poo)(poo)(poo)", "glhf (happy)", "glhf (hearts)", "gtfo noob",
              "gl youre gonna need it"] 

    #splits workers - can be improved in the future
    def worker_split(self):
        for w in self.workers:
            w.gather(self.mineral_field.closest_to(w))