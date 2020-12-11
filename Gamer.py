import asyncio
import logging
import random
import threading

import aiohttp

from Minimax import Minimax
from monkey_patched.game import Game

# Init components
game = Game()


class Gamer:
    def __init__(self, connection_config, heuristic, local_game=None, player_num=None):
        self.heuristic = heuristic
        self._config = connection_config
        self._api_url = f"http://{self._config['ip']}:{self._config['port']}"
        self._session = aiohttp.ClientSession()
        self._game = game
        self.local_game = local_game
        self.player_num = player_num

    async def _prepare_player(self, team_name):
        logging.info(f'Prepare bot name:{team_name}')
        async with self._session.post(
                f'{self._api_url}/game',
                params={'team_name': team_name}
        ) as resp:
            res = (await resp.json())['data']
            self._color = res['color']
            self._token = res['token']
            logging.info(f"The bot was prepared. Bot color: {self._color}")

    async def _make_move(self, move):
        logging.info(f"Send own move ({move}) to server")
        json = {'move': move}
        headers = {'Authorization': f'Token {self._token}'}
        async with self._session.post(
                f'{self._api_url}/move',
                json=json,
                headers=headers
        ) as resp:
            resp = (await resp.json())['data']
            logging.debug(f'Response from server: {resp}')

    async def _get_progress_game(self):
        async with self._session.get(f'{self._api_url}/game') as resp:
            logging.debug(f'Response status: {resp.status}')
            return (await resp.json())['data']

    def start(self):
        asyncio.run_coroutine_threadsafe(self.start_playing_on_server(), self._loop)

    async def start_playing_on_server(self):
        logging.basicConfig(level=logging.getLevelName(self._config['logging']),
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S')
        logging.info(f"Start bot {self._config['name']}")
        await self._prepare_player(self._config['name'])
        while True:
            current_game_progress = await self._get_progress_game()
            is_finished = current_game_progress['is_finished']
            if is_finished:
                logging.info("Game is finished")
                break

            is_started = current_game_progress['is_started']
            if current_game_progress['whose_turn'] == self._color:
                await self.move(current_game_progress)
            elif is_started:
                await asyncio.sleep(float(self._config['timeout']))

        await self._session.close()

    async def move(self, current_game_progress):
        if current_game_progress['whose_turn'] != self._color:
            logging.error("Not my turn")
            return
        self.read_opponent_move(current_game_progress)

        move = self.find_best_move(current_game_progress['available_time'], self._game)
        #move = random.choice(self._game.get_possible_moves())
        # await asyncio.sleep(2.0)
        logging.debug(f"Add move ({move}) to own game")
        self._game.move(move)
        await self._make_move(move)
        logging.info("")

    def read_opponent_move(self, current_game_progress):
        opponent_move = current_game_progress['last_move']
        if opponent_move is not None:
            logging.info(f"Read opponent move :{opponent_move}")
            if opponent_move['player'] != self._color:
                for move in opponent_move['last_moves']:
                    self._game.move(move)

    async def try_move_on_local(self):
        if self.local_game.is_over():
            await self._session.close()
            return
        if self.local_game.whose_turn() == self.player_num:
            #self.local_game.move(random.choice(self.local_game.get_possible_moves()))
            self.local_game.move(self.find_best_move(self._config['time_to_move'], self.local_game))

    def find_best_move(self, available_time, enter_game):
        logging.debug(f"Try find best local move with available_time = {available_time}")
        return Minimax().find_best_move(available_time, enter_game, self.heuristic)
