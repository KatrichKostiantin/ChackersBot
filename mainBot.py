import asyncio
import pathlib

import yaml

from Gamer import Gamer

BASE_DIR = pathlib.Path(__file__).parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'connection-config.yaml'

if __name__ == '__main__':
    with open(DEFAULT_CONFIG_PATH) as file:
        connection_config = yaml.load(file, Loader=yaml.FullLoader)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Gamer(connection_config, loop).start_playing())
