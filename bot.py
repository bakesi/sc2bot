import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, \
ASSIMILATOR, GATEWAY, CYBERNETICSCORE, STALKER

def log(message):
    print("BOT: " + message)

class ProtossBot(sc2.BotAI):
    async def on_step(self, iteration):
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offesive_force()

    async def build_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            if self.can_afford(PROBE):
                log("Training probe")
                await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
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
            if self.units(GATEWAY).exists:
                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        log("Bulding cyberneticscore")
                        await self.build(CYBERNETICSCORE, near=pylon)
            else:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    log("Building gateway")
                    await self.build(GATEWAY, near=pylon)

    async def build_offesive_force(self):
        if self.units(CYBERNETICSCORE).ready.exists:
            for gw in self.units(GATEWAY).ready.noqueue:
                if(self.can_afford(STALKER)):
                    log("Training stalker")
                    await self.do(gw.train(STALKER))

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, ProtossBot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=False)
