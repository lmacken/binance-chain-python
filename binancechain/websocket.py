# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
Binance DEX WebSockets

https://docs.binance.org/api-reference/dex-api/ws-streams.html#websocket-streams
"""
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp
import orjson
from pyee import AsyncIOEventEmitter

log = logging.getLogger(__name__)

MAINNET_URL = "wss://dex.binance.org/api/ws"
TESTNET_URL = "wss://testnet-dex.binance.org/api/ws"


class WebSocket:
    """The Binance DEX WebSocket Manager."""

    def __init__(
        self,
        address: str = None,
        testnet: bool = False,
        keepalive: bool = True,
        loop: asyncio.AbstractEventLoop = None,
        url: str = None,
    ) -> None:
        if not url:
            self.url = TESTNET_URL if testnet else MAINNET_URL
        else:
            self.url = url
        self.address = address
        self._session = aiohttp.ClientSession()
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._loop = loop or asyncio.get_event_loop()
        self._events = AsyncIOEventEmitter(loop=self._loop)
        self._sub_queue: List[Tuple[str, dict]] = []
        self._keepalive = keepalive
        self._keepalive_task: Optional[asyncio.Future] = None
        self._open = False
        self._testnet = testnet

    def on(self, event: str, func: Optional[Callable] = None, **kwargs):
        """Register an event, and optional handler.

        This can be used as a decorator or as a normal method.
        See `examples/websockets_decorator.py` for usage.
        """
        # Queue up most events from startup-time decorators until after we are open
        if not self._open and event not in ("open", "error", "new_listener"):
            self._sub_queue.append((event, kwargs))
        if func:
            self._events.on(event, func)
            return None
        else:
            return self._events.on(event)

    def start(
        self,
        on_open: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[dict], None]] = None,
        loop: asyncio.AbstractEventLoop = None,
    ) -> None:
        """The main blocking call to start the WebSocket connection."""
        loop = loop or asyncio.get_event_loop()
        return loop.run_until_complete(self.start_async(on_open, on_error))

    async def start_async(
        self,
        on_open: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[dict], None]] = None,
    ) -> None:
        """Processes all websocket messages."""
        if self.address:  # address-specific socket
            url = f"{self.url}/{self.address}"
        else:
            url = self.url

        async with self._session.ws_connect(url) as ws:
            self._ws = ws
            self._events.emit("open")
            while self._sub_queue:
                event, kwargs = self._sub_queue.pop()
                self.subscribe(event, **kwargs)
            if on_open:
                on_open()

            # Schedule keepalive calls every 30 minutes
            if self._keepalive:
                self._keepalive_task = asyncio.ensure_future(self._auto_keepalive())

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = msg.json(loads=orjson.loads)
                    except Exception as e:
                        log.error(f"Unable to decode msg: {msg}")
                        continue
                    if not data:
                        log.error(f"Got empty msg: {msg}")
                        continue
                    if "error" in data:
                        self._events.emit("error", data)
                        if on_error:
                            on_error(data)
                        else:
                            log.error(f"Unhandled error msg: {data}")
                        continue
                    if "stream" not in data:
                        log.error(f"Got msg without stream: {data}")
                        continue
                    if "data" not in data:
                        log.error(f"Got msg without data: {data}")
                        continue

                    self._events.emit(data["stream"], data)

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    log.error(msg)
                    self._events.emit("error", msg)
                    break

    async def send(self, data: dict) -> None:
        """Send data to the WebSocket"""
        if not self._ws:
            log.error("Error: Cannot send to uninitialized websocket")
            return
        await self._ws.send_bytes(orjson.dumps(data))

    def subscribe(
        self,
        stream: str,
        symbols: Optional[List[str]] = None,
        address: Optional[str] = None,
        callback: Optional[Callable[[dict], None]] = None,
    ):
        """Subscribe to a WebSocket stream.

        See the documentation for more details on the available streams
        https://docs.binance.org/api-reference/dex-api/ws-streams.html
        """
        payload: Dict[Any, Any] = {"method": "subscribe", "topic": stream}
        if symbols:
            payload["symbols"] = symbols
        if address:
            payload["address"] = address
        elif self.address:
            payload["address"] = self.address
        self._events.on(stream, callback)
        asyncio.ensure_future(self.send(payload))

    def unsubscribe(self, stream, symbols=None) -> None:
        payload = {"method": "unsubscribe", "topic": stream}
        if symbols:
            payload["symbols"] = symbols
        asyncio.ensure_future(self.send(payload))

    def subscribe_user_orders(
        self, callback: Callable[[dict], None], address: Optional[str] = None
    ) -> None:
        """Subscribe to individual order updates."""
        self.subscribe("orders", address=address, callback=callback)

    def subscribe_user_accounts(
        self, callback: Callable[[dict], None], address: Optional[str] = None
    ) -> None:
        """Subscribe to account updates."""
        self.subscribe("accounts", address=address, callback=callback)

    def subscribe_user_transfers(
        self, callback: Callable[[dict], None], address: Optional[str] = None
    ) -> None:
        """
        Subscribe to transfer updates if `address` is involved (as sender or
        receiver) in a transfer. Multisend is also covered.
        """
        self.subscribe("transfers", address=address, callback=callback)

    def subscribe_trades(
        self, symbols: List[str], callback: Callable[[dict], None]
    ) -> None:
        """Subscribe to individual trade updates."""
        self.subscribe("trades", symbols=symbols, callback=callback)

    def subscribe_market_diff(
        self, symbols: List[str], callback: Callable[[dict], None]
    ) -> None:
        "Order book price and quantity depth updates used to locally keep an order book." ""
        self.subscribe("marketDiff", symbols=symbols, callback=callback)

    def subscribe_market_depth(
        self, symbols: List[str], callback: Callable[[dict], None]
    ) -> None:
        """Top 20 levels of bids and asks."""
        self.subscribe("marketDepth", symbols=symbols, callback=callback)

    def subscribe_kline(
        self, interval: str, symbols: List[str], callback: Callable[[dict], None]
    ) -> None:
        """
        The kline/candlestick stream pushes updates to the current
        klines/candlestick every second.

        Kline/Candlestick chart intervals:
            m -> minutes; h -> hours; d -> days; w -> weeks; M -> months
            1m 3m 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M
        """
        self.subscribe(f"kline_{interval}", symbols=symbols, callback=callback)

    def subscribe_ticker(
        self, symbols: List[str], callback: Callable[[dict], None]
    ) -> None:
        """24hr Ticker statistics for a single symbol are pushed every second."""
        self.subscribe("ticker", symbols=symbols, callback=callback)

    def subscribe_all_tickers(self, callback: Callable[[dict], None]) -> None:
        """24hr Ticker statistics for a all symbols are pushed every second."""
        self.subscribe("allTickers", symbols=["$all"], callback=callback)

    def subscribe_mini_ticker(
        self, symbols: List[str], callback: Callable[[dict], None]
    ) -> None:
        """A ticker for a single symbol is pushed every second."""
        self.subscribe("miniTicker", symbols=symbols, callback=callback)

    def subscribe_all_mini_tickers(self, callback: Callable[[dict], None]) -> None:
        """Array of 24hr Mini Ticker statistics for a all symbols pushed every second."""
        self.subscribe("allMiniTickers", symbols=["$all"], callback=callback)

    def subscribe_blockheight(self, callback: Callable[[dict], None]) -> None:
        """Streams the latest block height."""
        self.subscribe("blockheight", symbols=["$all"], callback=callback)

    def keepalive(self) -> None:
        """Extend the connection time by another 30 minutes"""
        asyncio.ensure_future(self.send({"method": "keepAlive"}))

    async def _auto_keepalive(self):
        while True:
            await asyncio.sleep(30 * 60)
            self.keepalive()

    def close(self) -> None:
        """Close the websocket session"""
        asyncio.ensure_future(self.send({"method": "close"}))
        if self._session:
            asyncio.ensure_future(self._session.close())
        if self._keepalive_task:
            self._keepalive_task.cancel()
