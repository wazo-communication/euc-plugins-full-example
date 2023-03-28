# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .controller import Controller
from .config import load_config


def main():
    config = load_config()
    controller = Controller(config)
    controller.start()
    controller.run()

if __name__ == '__main__':
    main()
