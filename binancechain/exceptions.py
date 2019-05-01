# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT

import aiohttp

from typing import Optional


class BinanceChainException(Exception):
    def __init__(self, response: Optional[aiohttp.ClientResponse] = None):
        self.response = response

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.response}>"
