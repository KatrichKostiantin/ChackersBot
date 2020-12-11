import asyncio
import itertools
import pathlib

import yaml

from Battleground import Battleground
from Gamer import game, Gamer
from Heuristic import Heuristic
from Minimax import Node
from monkey_patched.game import Game

BASE_DIR = pathlib.Path(__file__).parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'local-config.yaml'


class Test:
    async def test(self):
        with open(DEFAULT_CONFIG_PATH) as file:
            local_config = yaml.load(file, Loader=yaml.FullLoader)

        heuristic_1 = Heuristic(1, 1, 1, 1, 0, 0)
        heuristic_2 = Heuristic(1, 3, 1, 3, 0, 0)
        # loop.run_until_complete(Battleground().start_one_battle(heuristic_1, heuristic_2))

        await asyncio.gather(
            Battleground().start_one_battle(heuristic_1, heuristic_2),
            Battleground().start_one_battle(heuristic_1, heuristic_2),
            Battleground().start_one_battle(heuristic_1, heuristic_2),
            Battleground().start_one_battle(heuristic_1, heuristic_2)
        )

        print("END")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Test().test())
