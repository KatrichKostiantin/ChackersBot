import asyncio
import pathlib

import yaml

from Gamer import Gamer
from Heuristic import Heuristic

BASE_DIR = pathlib.Path(__file__).parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'connection-config.yaml'

if __name__ == '__main__':
    with open(DEFAULT_CONFIG_PATH) as file:
        connection_config = yaml.load(file, Loader=yaml.FullLoader)
    loop = asyncio.get_event_loop()

    heuristic_1 = Heuristic(1, 1, 1, 1, 0, 0)
    heuristic_2 = Heuristic(1, 3, 1, 3, 0, 0)
    loop.run_until_complete(Gamer(connection_config, heuristic_2, None, None).start_playing_on_server())
