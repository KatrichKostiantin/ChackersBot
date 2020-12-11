import asyncio
import itertools
import logging
import pathlib
import threading
from datetime import datetime

import yaml

from Gamer import Gamer
from Heuristic import Heuristic
from monkey_patched.game import Game

BASE_DIR = pathlib.Path(__file__).parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'local-config.yaml'


class Battleground:

    async def start(self, heuristic_1, heuristic_2):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S')
        futures_list = list()

        win_counter_1 = FastReadCounter()
        win_counter_2 = FastReadCounter()
        self.start_n_battles(heuristic_1, heuristic_2, futures_list, win_counter_1, win_counter_2)
        await asyncio.gather(*futures_list)

        logging.info(f"End all battles at {datetime.now()}")
        logging.info(f"win_counter_1 = {win_counter_1.value}, win_counter_2 = {win_counter_2.value}")

    def start_n_battles(self, heuristic_1, heuristic_2, futures_list, win_counter_1, win_counter_2):
        logging.info(f"Start all battles at {datetime.now()}")
        for i in itertools.repeat(None, 2):
            futures = asyncio.create_task(self.start_one_battle(heuristic_1, heuristic_2))
            futures.add_done_callback(lambda f: self.__win(f.result(), win_counter_1, win_counter_2))
            futures.set_name(f"future {i}")
            futures_list.append(futures)

    def __win(self, res, win_counter_1, win_counter_2):
        if res == 1:
            win_counter_1.increment()
        elif res == 2:
            win_counter_2.increment()

    async def start_one_battle(self, heuristic_1, heuristic_2):
        logging.info(f"Start battle at {datetime.now()}")
        await asyncio.sleep(0)
        with open(DEFAULT_CONFIG_PATH) as file:
            local_config = yaml.load(file, Loader=yaml.FullLoader)
        game = Game()
        gamer_1 = Gamer(local_config, heuristic_1, game, 1)
        gamer_2 = Gamer(local_config, heuristic_2, game, 2)

        while True:
            if game.is_over():
                break
            await gamer_1.try_move_on_local()
            await gamer_2.try_move_on_local()

        await gamer_1.try_move_on_local()
        await gamer_2.try_move_on_local()
        logging.info(f"End battle at {datetime.now()}. Winner = {game.get_winner()}")
        return game.get_winner()


class FastReadCounter(object):
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self.value += 1


if __name__ == '__main__':
    heuristic_1 = Heuristic(1, 1, 1, 1, 0, 0)
    heuristic_2 = Heuristic(1, 3, 1, 3, 0, 0)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Battleground().start(heuristic_1, heuristic_2))
