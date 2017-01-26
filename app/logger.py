# -*- coding: utf-8 -*-
"""
    logger
    ~~~~~~

    This is the logger configuration module for SIGAS SGS.

    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña.
    :license: GPL v3.0, see LICENSE for more details.

"""
# Standard lib imports
import logging.handlers
import sys
# Third Party imports
from rainbow_logging_handler import RainbowLoggingHandler
# BITSON imports

console_logger = logging.getLogger('domi')
console_logger.setLevel(logging.DEBUG)

console_handler = RainbowLoggingHandler(sys.stderr)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(fmt="%(message)s"))

console_logger.addHandler(console_handler)
