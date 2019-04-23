"""
https://docs.binance.org/api-reference/dex-api/ws-streams.html#websocket-streams
"""
import asyncio
import json
import sys
from typing import Coroutine, Dict, List

import aiohttp

MAINNET_URL = ""
TESTNET_URL = "wss://testnet-dex.binance.org/api/ws"


class BinanceDexSocketManager:
    """The Binance DEX WebSocket Manager.

    API modeled off of `python-binance`.
    https://python-binance.readthedocs.io/en/latest/websockets.html
    """

    def __init__(self, testnet=False) -> None:
        self.url = TESTNET_URL if testnet else MAINNET_URL
        self.session = aiohttp.ClientSession()
        self.callbacks: Dict[str, Coroutine] = {}

    def start(self, on_open=None, on_error=None, loop=None):
        loop = loop or asyncio.get_event_loop()
        return loop.run_until_complete(self._start(on_open, on_error))

    async def _start(self, on_open, on_error):
        async with self.session.ws_connect(self.url) as ws:
            self.running = True
            self.ws = ws
            if on_open:
                on_open()
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = msg.json()
                    except Exception as e:
                        print(f"Unable to decode msg: {msg}", file=sys.stderr)
                        continue
                    if "error" in data:
                        if on_error:
                            on_error(data)
                        else:
                            print(f"Unhandled error msg: {data}", file=sys.stderr)
                        continue
                    if "stream" not in data:
                        print(f"Got msg without stream: {data}", file=sys.stderr)
                        continue
                    stream = data["stream"]
                    if stream not in self.callbacks:
                        print(
                            f"Cannot find callback for stream {stream}", file=sys.stderr
                        )
                        continue
                    self.callbacks[stream](data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(msg, file=sys.stderr)
                    break

    async def send(self, data: dict):
        """Send data to the WebSocket"""
        return await self.ws.send_str(json.dumps(data))

    def subscribe(self, stream, symbols=None, address=None, callback=None):
        """Subscribe to a WebSocket stream.

        See the documentation for more details on the available streams
        https://docs.binance.org/api-reference/dex-api/ws-streams.html
        """
        if not self.ws:
            print(
                "Cannot subscribe to stream before websocket is initialized.",
                file=sys.stderr,
            )
            return
        payload = {"method": "subscribe", "topic": stream}
        if symbols:
            payload["symbols"] = symbols
        if address:
            payload["userAddress"] = address
        self.callbacks[stream] = callback
        asyncio.ensure_future(self.send(payload))

    def unsubscribe(self, stream, symbols=None):
        if not self.ws:
            print(
                "Cannot subscribe to stream before websocket is initialized.",
                file=sys.stderr,
            )
            return
        payload = {"method": "unsubscribe", "topic": stream}
        if symbols:
            payload["symbols"] = symbols
        asyncio.ensure_future(self.send(payload))

    def subscribe_trades(self, symbols: List[str]) -> None:
        """Returns individual trade updates."""
        self.subscribe("trades", symbols=symbols)

    def subscribe_market_diff(self, symbols: List[str]) -> None:
        "Order book price and quantity depth updates used to locally keep an order book."""
        self.subscribe("marketDiff", symbols=symbols)

    def subscribe_market_depth(self, symbols: List[str]) -> None:
        """Top 20 levels of bids and asks."""
        self.subscribe("marketDepth", symbols=symbols)

    def subscribe_kline(self, interval: str, symbols: List[str]) -> None:
        """
        The kline/candlestick stream pushes updates to the current
        klines/candlestick every second.

        Kline/Candlestick chart intervals:
            m -> minutes; h -> hours; d -> days; w -> weeks; M -> months
            1m 3m 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M
        """
        self.subscribe(f"kline_{interval}", symbols=symbols)

    def subscribe_ticker(self, symbols: List[str]) -> None:
        """24hr Ticker statistics for a single symbol are pushed every second."""
        self.subscribe("ticker", symbols=symbols)

    def subscribe_all_tickers(self) -> None:
        """24hr Ticker statistics for a all symbols are pushed every second."""
        self.subscribe("allTickers", symbols=["$all"])

    def subscribe_mini_ticker(self, symbols: List[str]) -> None:
        """A ticker for a single symbol is pushed every second."""
        self.subscribe("miniTicker", symbols=symbols)

    def subscribe_all_mini_tickers(self) -> None:
        """Array of 24hr Mini Ticker statistics for a all symbols pushed every second."""
        self.subscribe("allMiniTickers", symbols=["$all"])

    def subscribe_blockheight(self) -> None:
        """Streams the latest block height."""
        self.subscribe("blockheight", symbols=["$all"])

    """
    TODO: user streams, where it needs a seperate /ws/<addy> connection

    Topic Name: orders | Stream: /ws/userAddress
        { method: "subscribe", topic: "orders", userAddress: "bnc1hp7cves62dzj8n4z8ckna0d3t6zd7z2zcj6gtq" }

    Topic Name: accounts | Stream: /ws/userAddress
        { method: "subscribe", topic: "accounts", userAddress: "bnc1hp7cves62dzj8n4z8ckna0d3t6zd7z2zcj6gtq" }


    Topic Name: transfers | Stream: /ws/userAddress
        { method: "subscribe", topic: "transfers", userAddress: "bnb1z220ps26qlwfgz5dew9hdxe8m5malre3qy6zr9" }
    """


if __name__ == "__main__":
    dex = BinanceDexSocketManager(testnet=True)

    def on_open():
        dex.subscribe("allMiniTickers", symbols=["$all"], callback=mini_tickers)

    def mini_tickers(msg):
        print("mini_tickers:", msg)

    def on_error(msg):
        print("! on_error", msg)

    dex.start(on_open, on_error)
