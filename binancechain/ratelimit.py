# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT

import asyncio

from typing import Dict, Tuple


class RateLimiter:
    """A rate-limiter that manages a token bucket for each namespace"""

    def __init__(self, period: int = 1):
        """
        :param period: How often this rate limiter will wake up to fill
        the token buckets. Defaults to once a second.
        """
        self.buckets: Dict[str, Tuple[asyncio.Queue, int]] = {}
        self.period = period
        self.task = None

    def close(self):
        if self.task:
            self.task.cancel()

    async def token_manager(self):
        """Fills each of the token buckets at `self.period` intervals."""
        while True:
            await asyncio.sleep(self.period)
            for queue, num in self.buckets.values():
                for i in range(num - queue.qsize()):
                    queue.put_nowait(1)

    async def limit(self, namespace, num):
        """Blocks for a given `namespace`, rate-limiting appropriately"""
        if namespace not in self.buckets:
            queue = asyncio.Queue(num)
            self.buckets[namespace] = (queue, num)
            for _ in range(num):
                queue.put_nowait(1)
            if not self.task:
                self.task = asyncio.ensure_future(self.token_manager())
                # Let the manager begin it's sleep cycle
                await asyncio.sleep(0.001)
        else:
            queue = self.buckets[namespace][0]
        await queue.get()
