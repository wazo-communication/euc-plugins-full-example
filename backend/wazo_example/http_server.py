# Copyright 2023 The Wazo Authors (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .http_router import router

app = FastAPI(
    title='application',
    openapi_url='/api/api.yml',
    redoc_url=None,
    docs_url=None
)


class Application:
    def __init__(self, config: dict = None):
        self.config: dict = config
        self.setup_static()
        self.setup_cors()
        app.include_router(router)

    def setup_static(self, path: str = "/data") -> None:
        app.mount("/content", StaticFiles(directory=path), name="static")

    def setup_cors(self) -> None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def run(self, host="0.0.0.0", port=8888) -> None:
        uvicorn.run(app, host=host, port=port, log_level="info", reload=False)
