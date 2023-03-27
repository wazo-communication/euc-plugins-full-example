# Copyright 2023 The Wazo Authors (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .http_router import router


class Application:
    def __init__(self, config: dict = None):
        self.app = FastAPI(
            title='application',
            openapi_url='/api/api.yml',
            redoc_url=None,
            docs_url=None
        )

        self.config: dict = config
        self.setup_static()
        self.setup_cors()
        self.app.include_router(router)

    def setup_static(self, path: str = "/data") -> None:
        self.app.mount("/content", StaticFiles(directory=path), name="static")

    def setup_cors(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
        )

    def load_app(self) -> FastAPI:
        return self.app

    def run(self, host="0.0.0.0", port=8888) -> None:
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info",
            reload=False
        )
