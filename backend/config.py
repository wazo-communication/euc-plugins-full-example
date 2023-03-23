# Copyright 2023 The Wazo Authors (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import yaml

from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    with open('config/config.yml') as file:
        return yaml.load(file, yaml.Loader)
