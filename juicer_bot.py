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
    
class JuicerBot(sc2.BotAI):
    #this is done at start of game
    async def on_start(self):
        #splits workers
        for w in self.workers:
            w.gather(self.mineral_field.closest_to(w))
        
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

    #testing how to slowly have a unit move up the ramp
    async def on_step(self, iteration):
        if iteration == 0:
            worker = self.workers.random
            self.scoutworker = worker
            worker.move(self.proxyvar)

       #if we started the attack, select the zealots and have them go  
        if self.scoutworker:
            self.scoutworker.attack(self.scoutworker.position.towards(self.enemy_start_locations[0], 2))

    """
    #on_step is essentially each frame of the game
    async def on_step(self, iteration):

        #first hatchery
        hatch = self.townhalls[0]

        #hard code 13/12 opener
        if not (self.already_pending(UnitTypeId.SPAWNINGPOOL) or self.structures(UnitTypeId.SPAWNINGPOOL).ready):
            if (self.supply_used == 13 and self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) == 0 and self.can_afford(UnitTypeId.EXTRACTOR)):
                worker = self.workers[0]
                gas = self.vespene_geyser.closest_to(worker)
                worker = self.workers.closest_to(gas)
                if worker.is_carrying_minerals:
                    worker.return_resource()
                    worker.build_gas(gas, queue=True)
                else:
                    worker.build_gas(gas)

            #gas_buildings may return 1 for building gas buildings as well, documentation doesn't specify so added both for safety
            if (self.supply_used == 12 and (self.already_pending(UnitTypeId.EXTRACTOR) == 1 or self.gas_buildings == 1)):
                if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                    map_center = self.game_info.map_center
                    position_towards_map_center = self.start_location.towards(map_center, distance=5)
                    placement_position = await self.find_placement(UnitTypeId.SPAWNINGPOOL, near=position_towards_map_center, placement_step=1)
                    worker = self.workers.random
                    while(not worker.is_carrying_minerals):
                        worker = self.workers.random

                    # Placement_position can be None
                    if placement_position:
                        worker.return_resource()
                        worker.build(UnitTypeId.SPAWNINGPOOL, placement_position)
            
            elif (self.supply_used == 12 and self.gas_buildings.amount + self.already_pending(UnitTypeId.EXTRACTOR) == 0):
                self.train(UnitTypeId.DRONE)

            if self.gas_buildings.ready and self.vespene < 88 and not self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED):
                gas = self.gas_buildings.first
                if gas.surplus_harvesters < 0:
                    worker = self.workers.random
                    if worker.is_carrying_minerals:
                        worker.return_resource()
                        worker.gather(gas, queue=True)
                    worker.gather(gas)

        #rest of build
        else:

            if self.supply_used < 14 and self.supply_left > 0:
                self.train(UnitTypeId.DRONE)

            if not self.already_pending(UnitTypeId.OVERLORD) and self.supply_left == 0:
                self.train(UnitTypeId.OVERLORD, 1)
        
            #putting the boys on the gas geysers
            if self.gas_buildings.ready and self.vespene < 88 and not self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED):
                gas = self.gas_buildings.first
                if gas.surplus_harvesters < 0:
                    worker = self.workers.random
                    if worker.is_carrying_minerals:
                        worker.return_resource()
                        worker.gather(gas, queue=True)
                    worker.gather(gas)
            
            # Pull workers out of gas if we have almost enough gas mined, this will stop mining when we reached 100 gas mined
            #copied from https://github.com/BurnySc2/python-sc2/blob/develop/examples/zerg/zerg_rush.py
            if self.vespene >= 88 or self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) > 0:
                gas_drones: Units = self.workers.filter(lambda w: w.is_carrying_vespene and len(w.orders) < 2)
                drone: Unit
                for drone in gas_drones:
                    minerals: Units = self.mineral_field.closer_than(10, hatch)
                    if minerals:
                        mineral: Unit = minerals.closest_to(drone)
                        drone.gather(mineral, queue=True)

            #try to research zergling speed
            #copied from https://github.com/BurnySc2/python-sc2/blob/develop/examples/zerg/zerg_rush.py
            if self.structures(UnitTypeId.SPAWNINGPOOL).ready and self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0:
                if self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
                    self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)
            #if self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) == 0 and self.can_afford(UpgradeId.ZERGLINGMOVEMENTSPEED):
            #    spawning_pools_ready: Units = self.structures(UnitTypeId.SPAWNINGPOOL).ready
            #    if spawning_pools_ready:
            #        self.research(UpgradeId.ZERGLINGMOVEMENTSPEED)

            #mass lings and inject the hatchery
            #start queen    
            # Build queen once the pool is done
            if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
                if not self.units(UnitTypeId.QUEEN) and not self.already_pending(UnitTypeId.QUEEN):
                    if self.can_afford(UnitTypeId.QUEEN):
                        hatch.train(UnitTypeId.QUEEN)
            #INJECT
            for queen in self.units(UnitTypeId.QUEEN).idle:
                if queen.energy >= 25:
                    queen(AbilityId.EFFECT_INJECTLARVA, hatch)

            #make ovies when needed
            if self.supply_left == 2 and not self.already_pending(UnitTypeId.OVERLORD):
                self.train(UnitTypeId.OVERLORD, 1)

            #make zerglings
            if self.larva and self.can_afford(UnitTypeId.ZERGLING) and self.structures(UnitTypeId.SPAWNINGPOOL).ready:
                self.train(UnitTypeId.ZERGLING, self.larva)

            #start the attack
            if self.already_pending_upgrade(UpgradeId.ZERGLINGMOVEMENTSPEED) > .8:
                for zergling in self.units(UnitTypeId.ZERGLING).idle:
                    zergling.attack(self.enemy_start_locations[0])


            #offensive gg       not working
            #if self.state.chat:
             #   for chat in self.state.chat:
              #      if chat.message == "gg":
               #         await self.chat_send('ez noob')
    """

    #chooses a random start message
    def start_message(self):
        return ["(glhf)", "(poo)(poo)(poo)", "glhf (happy)", "glhf (hearts)", "gtfo noob",
              "gl youre gonna need it"] 
        
