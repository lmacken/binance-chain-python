"""
https://docs.binance.org/api-reference/dex-api/ws-streams.html#websocket-streams
"""
import asyncio
import sys
from typing import Any, Callable, Dict, List, Optional

import aiohttp

MAINNET_URL = ""
TESTNET_URL = "wss://testnet-dex.binance.org/api/ws"


class BinanceDexSocketManager:
    """The Binance DEX WebSocket Manager."""

    def __init__(self, testnet: bool = False) -> None:
        self.url = TESTNET_URL if testnet else MAINNET_URL
        self._session = aiohttp.ClientSession()
        self._callbacks: Dict[str, Callable[[dict], None]] = {}
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None

    def start(
        self,
        on_open: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[dict], None]] = None,
        loop: asyncio.AbstractEventLoop = None,
    ) -> None:
        """The main blocking call to start the WebSocket connection."""
        loop = loop or asyncio.get_event_loop()
        return loop.run_until_complete(self._start(on_open, on_error))

    async def _start(
        self,
        on_open: Optional[Callable[[], None]],
        on_error: Optional[Callable[[dict], None]],
    ) -> None:
        """Processes all websocket messages."""
        async with self._session.ws_connect(self.url) as ws:
            self._ws = ws
            if on_open:
                on_open()
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = msg.json()
                    except Exception as e:
                        print(f"Unable to decode msg: {msg}", file=sys.stderr)
                        continue
                    if not data:
                        print(f"Got empty msg: {msg}", file=sys.stderr)
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
                    if stream not in self._callbacks:
                        print(
                            f"Cannot find callback for stream {stream}", file=sys.stderr
                        )
                        continue
                    self._callbacks[stream](data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(msg, file=sys.stderr)
                    break

    async def send(self, data: dict) -> None:
        """Send data to the WebSocket"""
        if not self._ws:
            print("Error: Cannot send to uninitialized websocket", file=sys.stderr)
            return
        await self._ws.send_json(data)

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
            payload["userAddress"] = address
        if callback:
            self._callbacks[stream] = callback
        asyncio.ensure_future(self.send(payload))

    def unsubscribe(self, stream, symbols=None) -> None:
        payload = {"method": "unsubscribe", "topic": stream}
        if symbols:
            payload["symbols"] = symbols
        asyncio.ensure_future(self.send(payload))

    def subscribe_user_orders(
        self, address: str, callback: Callable[[dict], None]
    ) -> None:
        """Subscribe to individual order updates."""
        self.subscribe("orders", address=address, callback=callback)

    def subscribe_user_accounts(
        self, address: str, callback: Callable[[dict], None]
    ) -> None:
        """Subscribe to account updates."""
        self.subscribe("accounts", address=address, callback=callback)

    def subscribe_user_transfers(
        self, address: str, callback: Callable[[dict], None]
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


if __name__ == "__main__":
    dex = BinanceDexSocketManager(testnet=True)

    def on_open():
        address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
        dex.subscribe_user_orders(address, user_orders)
        dex.subscribe_user_accounts(address, user_orders)
        dex.subscribe_user_transfers(address, user_orders)

        # dex.subscribe("allMiniTickers", symbols=["$all"], callback=mini_tickers)

    def user_orders(msg):
        print(f"user_orders: {msg}")

    def user_accounts(msg):
        print(f"user_accounts: {msg}")

    def user_transfers(msg):
        print(f"user_transfers: {msg}")

    def mini_tickers(msg):
        print(f"mini_tickers: {msg}")

    def on_error(msg):
        print(f"Error: {msg}")

    dex.start(on_open, on_error)
