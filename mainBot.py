import asyncio
import threading

from Gamer import Gamer

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    threading.Thread(target=Gamer(loop).start).start()
    loop.run_forever()