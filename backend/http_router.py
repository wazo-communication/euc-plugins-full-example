# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from fastapi import APIRouter, WebSocket, Depends, Header
from starlette.websockets import WebSocketDisconnect
from typing import Optional, Dict, Any, List

from dependencies import auth, calls, wclient
from logger import setup_logging


logger = setup_logging()
router = APIRouter()

@router.get("/calls")
def list_calls(user_token: str = Depends(auth.get_and_verify_token)) -> List[Dict[str, Any]]:
    return calls.list_calls(user_token)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> Optional[bool]:
    await wclient.connect(websocket)

    try:
        while True:
            data = await wclient.receive_json(websocket)
            if not data:
                return False

            await wclient.handle_websocket_data(websocket, data, auth)
    except WebSocketDisconnect:
        logger.debug("Websocket from client has been disconnected")
        wclient.remove(websocket)
