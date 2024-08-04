"""Pylint plugin for checking the html f-string templates"""

# Licenced under the MIT License: https://www.opensource.org/licenses/mit-license.php

__version__ = "0.1.0"

from .plugin import HtmfChecker


def register(linter):
    linter.register_checker(HtmfChecker(linter))
