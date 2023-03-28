# -*- coding: utf-8 -*-
# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import json
import ssl
import asyncio
import websockets

from .exceptions import AlreadyConnectedException, NotRunningException


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


class websocketdClient:

    _url_fmt = '{scheme}://{host}{port}{prefix}'

    def __init__(
        self,
        host,
        port='',
        prefix='/api/websocketd',
        token=None,
        verify_certificate=True,
        wss=True,
        **kwargs
    ):
        self.host = host
        self._port = port
        self._prefix = prefix
        self._token_id = token
        self._wss = wss
        self._verify_certificate = verify_certificate

        self._ws_app = None
        self._is_running = False
        self._callbacks = {}
        self.logger = setup_logger(f"{__name__}.{id(self)}")

    def set_token(self, token):
        if self._is_running:
            raise AlreadyConnectedException()
        self._token_id = token

    async def subscribe(self, event_name):
        await self._ws_app.send(
            json.dumps({'op': 'subscribe', 'data': {'event_name': event_name}})
        )

    def on(self, event, callback):
        self._callbacks[event] = callback

    async def trigger_callback(self, event, data):
        if '*' in self._callbacks:
            await self._callbacks['*'](data)
        elif self._callbacks.get(event):
            await self._callbacks[event](data)

    async def _start(self):
        msg = {'op': 'start'}
        await self._ws_app.send(json.dumps(msg))

    async def init(self, msg):
        if msg.get('op') == 'init':
            for event in self._callbacks.keys():
                await self.subscribe(event)
            await self._start()

        if msg.get('op') == 'start':
            self._is_running = True

    def ping(self, payload):
        if not self._ws_app:
            raise NotRunningException()

        self._ws_app.send(json.dumps({'op': 'ping', 'data': {'payload': payload}}))

    async def on_message(self, ws, message):
        msg = json.loads(message)

        if not self._is_running:
            await self.init(msg)
        else:
            if msg.get('op') == 'event':
                await self.trigger_callback(msg['data']['name'], msg['data'])

    def on_error(self, ws, error):
        self.logger.error('WS encountered an error: %s: %s', type(error).__name__, error)
        if isinstance(error, KeyboardInterrupt):
            raise error

    def on_close(self, close_status_code, close_reason):
        if close_status_code and close_reason:
            self.logger.debug(
                'WS closed with code %s, reason: %s.',
                close_status_code,
                close_reason if close_reason else 'unknown',
            )
        elif close_status_code:
            self.logger.debug(
                'WS closed with code %s.',
                close_status_code,
            )
        else:
            self.logger.debug('WS closed.')
        self._is_running = False

    def on_open(self, ws):
        self.logger.debug('Starting connection ...')

    async def update_token(self, token):
        await self._ws_app.send(json.dumps({'op': 'token', 'data': {'token': token}}))

    def url(self):
        base = self._url_fmt.format(
            scheme='wss' if self._wss else 'ws',
            host=self.host,
            port=':{}'.format(self._port) if self._port else '',
            prefix=self._prefix,
        )
        return '{}/?version=2'.format(base)

    def headers(self):
        return [["X-Auth-Token", self._token_id]]

    async def run(self):
        while True:
            try:
                if not self._verify_certificate:
                    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                else:
                    ssl_context = True

                self._ws_app = await websockets.connect(
                    self.url(),
                    extra_headers=self.headers(),
                    ssl=ssl_context
                )

                self.logger.debug("Websocket connected")

                self.on_open(self._ws_app)

                while True:
                    msg = await self._ws_app.recv()
                    await self.on_message(self._ws_app, msg)

            except websockets.ConnectionClosed as e:
                self.on_close(4000, "Unknown Exception")
                await asyncio.sleep(2)
                continue
