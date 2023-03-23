# Copyright 2023 The Wazo Authors (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from typing import List, Dict, Any

from logger import setup_logging
from http_server import app, Application
from dependencies import wwebsocket, wclient


logger = setup_logging()


class Controller:
    def __init__(self, config: Dict[str, Any]):
        self.config: Dict[str, Any] = config
        self.http_server: Application = Application(config=config)

        logger.debug('Loaded routes:\n%s', self.list_routes())

    def list_routes(self) -> List[Dict[str, str]]:
        url_list: List[Dict[str, str]] = [{'path': route.path, 'name': route.name} for route in app.routes]
        return url_list

    def run(self) -> None:
        logger.info('Backend application is starting...')
        self.http_server.run()


async def queue_synchro(queue: asyncio.Queue) -> None:
    while True:
        try:
            data: Any = await queue.get()
            await wclient.send(data)
        except Exception as e:
            logger.error(f"An error occurred while processing the queue: {e}")

@app.on_event('startup')
async def app_startup() -> None:
    queue = asyncio.Queue()
    asyncio.ensure_future(queue_synchro(queue))
    asyncio.ensure_future(wwebsocket.run(queue))
