import asyncio
import logging

import aiohttp

from monkey_patched.game import Game

# Init components
game = Game()


class Gamer:
    def __init__(self, loop):
        self._api_url = 'http://localhost:8081'
        self._session = aiohttp.ClientSession()
        self._game = game
        self._loop = loop


    async def _prepare_player(self, team_name):
        async with self._session.post(
                f'{self._api_url}/game',
                params={'team_name': team_name}
        ) as resp:
            res = (await resp.json())['data']
            self._color = res['color'],
            self._token = res['token']


    async def _make_move(self, player, move):
        json = {'move': move}
        headers = {'Authorization': f'Token {self._token}'}
        async with self._session.post(
                f'{self._api_url}/move',
                json=json,
                headers=headers
        ) as resp:
            resp = (await resp.json())['data']
            logging.info(f'Player {player} made move {move}, response: {resp}')

    #current_game_progress = await self._get_game()
    #is_finished = current_game_progress['is_finished']
    #is_started = current_game_progress['is_started']


    async def _get_progress_game(self):
        async with self._session.get(f'{self._api_url}/game') as resp:
            return (await resp.json())['data']

    def start(self):
        self._prepare_player('BOT NAME')
        board = self._game.board
        self._game.board = board

if __name__ == '__main__':
    gamer = Gamer(asyncio.get_event_loop())
    gamer.start()
