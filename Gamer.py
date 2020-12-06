import asyncio
import logging
import random
import threading

import aiohttp

from monkey_patched.game import Game

# Init components
game = Game()


class Gamer:
    def __init__(self, connection_config, loop):
        self._api_url = f"http://{connection_config['ip']}:{connection_config['port']}"
        self._session = aiohttp.ClientSession()
        self._game = game
        self._loop = loop
        logging.basicConfig(level=logging.INFO)

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
        json = {'move': move}
        headers = {'Authorization': f'Token {self._token}'}
        async with self._session.post(
                f'{self._api_url}/move',
                json=json,
                headers=headers
        ) as resp:
            resp = (await resp.json())['data']
            logging.info(f'Response : {resp}')

    async def _get_progress_game(self):
        async with self._session.get(f'{self._api_url}/game') as resp:
            return (await resp.json())['data']

    def start(self):
        asyncio.run_coroutine_threadsafe(self.start_playing(), self._loop)

    async def start_playing(self):
        await self._prepare_player('BOT NAME')
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
                await asyncio.sleep(0.10)

        await self._session.close()

    async def move(self, current_game_progress):
        if current_game_progress['whose_turn'] != self._color:
            logging.error("Not my turn")
            return
        self.read_opponent_move(current_game_progress)

        move = random.choice(self._game.get_possible_moves())


        await asyncio.sleep(0.50)
        self._game.move(move)
        await self._make_move(move)

    def read_opponent_move(self, current_game_progress):
        opponent_move = current_game_progress['last_move']
        if opponent_move is not None:
            if opponent_move['player'] != self._color:
                for move in opponent_move['last_moves']:
                    self._game.move(move)
