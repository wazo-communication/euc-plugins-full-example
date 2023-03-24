
# Copyright 2023 The Wazo Authors (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

def setup_logging() -> logging:
    logger = logging.getLogger(__name__)
    LOG_FORMAT = '%(asctime)s (%(levelname)s) (%(name)s): %(message)s'
    logging.basicConfig(format=LOG_FORMAT)
    logger.setLevel(logging.DEBUG)

    return logger
