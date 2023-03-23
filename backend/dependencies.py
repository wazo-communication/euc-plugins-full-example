# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio

from config import load_config
from helpers import (
    WebSocketManager,
    AuthManager,
    CallManager,
    WazoWebSocket
)


config = load_config()
auth = AuthManager(config['host'])
calls = CallManager(config['host'])
wclient = WebSocketManager()
wwebsocket = WazoWebSocket(
    config['host'],
    config['username'],
    config['password'],
    auth
)
