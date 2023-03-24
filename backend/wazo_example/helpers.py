# Copyright 2023 The Wazo Authors (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import aiohttp
import asyncio
import logging
import json
import requests

from typing import Dict, Optional, Any
from fastapi import WebSocket, Header, HTTPException

from wazo_auth_client import Client as Auth
from wazo_calld_client import Client as Calld

from wazo_websocketd_async_client import Client as WWebSocket

from .logger import setup_logging

logger = setup_logging()


class AuthManager:
    def __init__(
            self,
            host: str,
            expiration: int = 3600,
            client_id: str = 'backend-plugin',
            verify_certificate: bool = False
        ):
        self.host: str = host
        self.expiration: int = expiration
        self.client_id: str = client_id
        self.verify_certificate: bool = verify_certificate
        self.token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_uuid: Optional[str] = None
        self.auth: Optional[Auth] = None

    def init(self, username: str, password: str) -> None:
        self.auth = Auth(
            self.host,
            username=username,
            password=password,
            verify_certificate=self.verify_certificate
        )
        self.get_refresh_token()

    def get_token_with_refresh_token(self, expired: bool = False) -> str:
        if self.token is None or expired:
            logger.debug('Create new token w/ refresh token')
            token_data = self.auth.token.new(
                "wazo_user",
                expiration=self.expiration,
                refresh_token=self.refresh_token,
                client_id=self.client_id,
            )
            self.token = token_data['token']

        return self.token

    def get_refresh_token(self) -> None:
        token_data = self.auth.token.new(
            "wazo_user",
            access_type="offline",
            client_id=self.client_id,
            expiration=self.expiration
        )
        self.refresh_token = token_data['refresh_token']
        self.token = token_data['token']
        self.user_uuid = token_data['metadata']['uuid']

    async def get_and_verify_token(self, x_auth_token: str = Header(default=None), use_async: bool = False) -> None:
        if use_async:
            token = None
            try:
                token = self.auth.token.get(x_auth_token)
                return token['metadata']['uuid']
            except requests.exceptions.HTTPError:
                raise HTTPException(status_code=401, detail="Authentication failed")
        else:
            async with aiohttp.ClientSession() as session:
                token_url = f'https://{self.host}/api/auth/0.1/token/{x_auth_token}'
                async with session.head(token_url) as resp:
                    if resp.status != 204:
                        raise HTTPException(status_code=401, detail="Authentication failed")

        return x_auth_token

    def session_has_expired(self, event: Dict) -> bool:
        session_user_uuid = event['data']['user_uuid']
        if session_user_uuid != self.user_uuid:
            return False

        logger.debug("session expired")
        token = self.get_token_with_refresh_token(expired=True)

        if token:
            self.auth.set_token(token)
            return True

        return False


class CallManager:
    def __init__(
            self,
            host: str,
            verify_certificate: bool = False
        ):
        self.host: str = host
        self.verify_certificate: bool = verify_certificate

    def list_calls(self, token: str) -> list:
        calld = Calld(self.host, token=token, verify_certificate=self.verify_certificate)
        return calld.calls.list_calls_from_user()


class WebSocketManager:
    def __init__(self):
        self.connections: Dict[int, Dict[WebSocket, str]] = {}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[id(websocket)] = {"ws": websocket}
        logger.debug("New user is connected")

    async def disconnect(self, websocket: WebSocket) -> None:
        await websocket.close()
        self.remove(websocket)
        logger.debug("Close websocket")

    async def receive_json(self, websocket: WebSocket) -> Optional[Dict[str, Any]]:
        try:
            data = await websocket.receive_json()
        except json.decoder.JSONDecodeError:
            logger.debug("Data from websocket client is not JSON")
            await self.disconnect(websocket)
            return None

        return data

    async def handle_websocket_data(self, websocket: WebSocket, data: Dict[str, Any], auth: AuthManager) -> None:
        if data and 'X-Auth-Token' in data:
            user_uuid = await auth.get_and_verify_token(data['X-Auth-Token'], True)
            self.connections[id(websocket)].update({"user_uuid": user_uuid})
        else:
            await self.disconnect(websocket)

    def remove(self, websocket: WebSocket) -> None:
        del self.connections[id(websocket)]
        logger.debug("Clean websocket")

    async def send(self, data: str) -> None:
        for connection in self.connections:
            ws = self.connections[connection]['ws']
            user_uuid = self.connections[connection]['user_uuid']
            if data['data']['user_uuid'] == user_uuid:
                await ws.send_json(data)

class WazoWebSocket:
    def __init__(
            self,
            host: str,
            username:str,
            password: str,
            auth: AuthManager,
            verify_certificate: bool = False
        ):
        self.host: str = host
        self.username: str = username
        self.password: str = password
        self.queue: asyncio.Queue = None
        self.auth: AuthManager = auth
        self.verify_certificate: bool = verify_certificate
        self.ws: WebSocket = None

    async def run(self, queue: asyncio.Queue) -> None:
        self.queue = queue
        self.auth.init(self.username, self.password)
        self.auth.get_token_with_refresh_token()

        logger.debug('Connect websocket client to Wazo')
        self.ws = WWebSocket(self.host, token=self.auth.token, verify_certificate=self.verify_certificate)
        self.ws.on('call_created', self.call_created)
        self.ws.on('auth_session_expire_soon', self.session_expired)
        await self.ws.run()

    async def call_created(self, handler: Dict[str, Any]) -> None:
        await self.notify(handler)

    async def notify(self, handler: Dict[str, Any]) -> None:
        await self.queue.put(handler)

    async def session_expired(self, handler: Dict[str, Any]) -> None:
        if self.auth.session_has_expired(handler):
            await self.ws.update_token(self.auth.token)
