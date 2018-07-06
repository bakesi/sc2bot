import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, \
ASSIMILATOR, GATEWAY, STARGATE, CYBERNETICSCORE, STALKER, VOIDRAY
import random

def log(message):
    print("BOT: " + message)

class ProtossBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE = 165
        self.MAX_WORKERS = 65

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offesive_force()
        await self.attack()

    async def build_workers(self):
        if len(self.units(NEXUS)) * 16 > len(self.units(PROBE)):
            if len(self.units(PROBE)) < self.MAX_WORKERS:
                for nexus in self.units(NEXUS).ready.noqueue:
                    if self.can_afford(PROBE):
                        log("Training probe")
                        await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 8 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists and self.can_afford(PYLON):
                log("Building pylon")
                await self.build(PYLON, near=nexuses.first)

    async def build_assimilators(self):
        for nexux in self.units(NEXUS).ready:
            vaspenses = self.state.vespene_geyser.closer_than(10.0, nexux)
            for vaspene in vaspenses:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    log("Building assimilator")
                    await self.do(worker.build(ASSIMILATOR, vaspene))

    async def expand(self):
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            log("Expanding")
            await self.expand_now()

    async def offensive_force_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            amount = self.units(GATEWAY).amount
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    log("Bulding cyberneticscore")
                    await self.build(CYBERNETICSCORE, near=pylon)
            elif amount < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2) and \
                 amount < 4 and amount <= self.units(STALKER).amount:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    log("Building gateway")
                    await self.build(GATEWAY, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists:
                amount = self.units(STARGATE).amount
                if amount < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2) and \
                    amount < 6 and amount <= self.units(VOIDRAY).amount:
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        log("Building stargate")
                        await self.build(STARGATE, near=pylon)

    async def build_offesive_force(self):
        if self.units(CYBERNETICSCORE).ready.exists:
            for gw in self.units(GATEWAY).ready.noqueue:
                if not self.units(STALKER).amount > self.units(VOIDRAY).amount:
                    if self.can_afford(STALKER) and self.supply_left > 0:
                        log("Training stalker")
                        await self.do(gw.train(STALKER))

        for sg in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                log("Training voidray")
                await self.do(sg.train(VOIDRAY))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        printedLog = False
        readyToAttack = True
        army = {STALKER: [15, 3],
                VOIDRAY: [8, 3]}
        for unit in army:
            if self.units(unit).amount < army[unit][0]:
                readyToAttack = False
        
        for unit in army:
            if readyToAttack:
                for s in self.units(unit).idle:
                    if not printedLog:
                        log("Attack! Get `em!")
                        printedLog = True
                    await self.do(s.attack(self.find_target(self.state)))
            elif self.units(unit).amount >= army[unit][1]:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(unit).idle:
                        if not printedLog:
                            log("Attack! Get `em!")
                            printedLog = True
                        await  self.do(s.attack(random.choice(self.known_enemy_units)))

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, ProtossBot()),
    Computer(
        Race.Terran,
        Difficulty.Hard
    )
], realtime=True)
