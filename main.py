import sc2, sys
from sc2 import Race, Difficulty
from sc2.player import Bot, Computer
#import maps


from juicer_bot import JuicerBot
from GruyereBot import GruyereBot
bot = Bot(Race.Protoss, GruyereBot())

if __name__ == '__main__':
    print("starting game")
    sc2.run_game(sc2.maps.get("AcropolisLE"),
                 [bot, Computer(Race.Protoss, Difficulty.VeryEasy)],
                 realtime=False)
