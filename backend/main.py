#!/usr/bin/env python3
# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from controller import Controller
from config import load_config
from logger import setup_logging


def main():
    config = load_config()
    logger = setup_logging()
    controller = Controller(config)
    controller.run()

if __name__ == '__main__':
    main()
