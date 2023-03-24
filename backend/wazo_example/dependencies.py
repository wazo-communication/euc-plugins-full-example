# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import os

from .config import load_config
from .helpers import (
    WebSocketManager,
    AuthManager,
    CallManager,
    WazoWebSocket
)


config = load_config()

host = config['host'] or os.getenv('WAZO_HOST')
username = config['username'] or os.getenv('WAZO_USERNAME')
password = config['password'] or os.getenv('WAZO_PASSWORD')

auth = AuthManager(host)
calls = CallManager(host)
wclient = WebSocketManager()
wwebsocket = WazoWebSocket(
    host,
    username,
    password,
    auth
)
