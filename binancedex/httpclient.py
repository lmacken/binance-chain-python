"""
    Interact with binance chain
"""
import asyncio
import sys
import traceback
import warnings
from typing import Any, List

import aiohttp

NETWORK_PREFIX_MAPPING = {"testnet": "tbnb", "mainnet": "bnb"}
API = [
    "time",
    "node-info",
    "validators",
    "peers",
    "account",
    "tx",
    "tokens",
    "markets",
    "fees",
    "depth",
    "broadcast",
    "klines",
    "orders",
    "ticker",
    "trades",
    "transactions",
]

MAINNET_URL = ""
TESTNET_URL = "https://testnet-dex.binance.org"


class BNC:
    """ Binance DEX Client """

    def __init__(
        self,
        testnet: bool = True,
        api_version: str = "v1",
        session: aiohttp.ClientSession = None,
    ):
        """
        :testnet: A boolean to enable testnet
        :api_version: The API version to use
        :session: An optional HTTP session to use
        """
        url = TESTNET_URL if testnet else MAINNET_URL
        self._server = f"{url}/api/{api_version}/"
        self._session = aiohttp.ClientSession()

    def __del__(self):
        if self._session:
            warnings.warn(f"{repr(self)}.close() was never awaited")

    async def close(self):
        """ Clean up our connections """
        if self._session:
            try:
                await self._session.close()
                self._session = None
            except Exception as e:
                traceback.print_exc()

    async def _request(self, method: str, path: str, **kwargs):
        """
        :method: `get` or `post`
        :path: the remote endpoint to call
        :kwargs: Extra arguments to pass to the request, like `params` or `data`.
        """
        try:
            async with getattr(self._session, method)(
                self._server + path, **kwargs
            ) as resp:
                return await resp.json()
        except Exception as e:
            print("Error:", await resp.text(), file=sys.stderr)

    async def get_request(self, path: str, params: dict = None) -> Any:
        return await self._request("get", path, params=params)

    async def post_request(self, path: str, data: dict = None) -> Any:
        return await self._request("post", path, data=data)

    async def get_balance(self, address: str):
        try:
            info = await self.get_account_info(address)
            return info["result"]["balance"]
        except Exception as e:
            return "No balance found"

    async def get_account_info(self, address: str):
        return await self.get_request(f"account/{address}")

    async def get_time(self) -> dict:
        """ Get the block time.

        Gets the latest block time and the current time according to the HTTP
        service.

        Destination: Validator node.
	Rate Limit: 1 request per IP per second.
        """
        return await self.get_request("time")

    async def get_node_info(self) -> dict:
        """ Get node information.

        Gets runtime information about the node.

        Destination: Validator node.
        Rate Limit: 1 request per IP per second.
        """
        return await self.get_request("node-info")

    async def get_validators(self) -> dict:
        """ Get validators.

        Gets the list of validators used in consensus.

        Destination: Witness node.
        Rate Limit: 10 requests per IP per second.
        """
        return await self.get_request("validators")

    async def get_peers(self) -> list:
        """  Get network peers.

        Gets the list of network peers.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.
        """
        return await self.get_request("peers")

    async def get_transaction(self, txid: str) -> dict:
        return await self.get_request(f"tx/{txid}")

    async def get_token_list(self) -> List[dict]:
        """ Get tokens list.

        Gets a list of tokens that have been issued.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.
        """
        return await self.get_request("tokens")

    async def get_markets(self, limit: int = 500, offset: int = 0) -> List[dict]:
        """
        :limit: default 500; max 1000.
        :offset: start with 0; default 0.
        """
        return await self.get_request(
            "markets", params={"limit": limit, "offset": offset}
        )

    async def get_fees(self) -> List[dict]:
        return await self.get_request("fees")

    async def get_depth(self, symbol: str, limit: int = 100):
        return await self.get_request(
            "depth", params={"symbol": symbol, "limit": limit}
        )

    async def broadcast(self, _signedTx):
        return self.post_request("broadcast", data=_signedTx)

    async def get_klines(
        self, symbol, interval, limit=300, startTime=None, endTime=None
    ):
        return self.get_request(
            "klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
                "startTime": startTime,
                "endTime": endTime,
            },
        )

    async def get_closed_orders(
        self,
        address,
        end=None,
        limit=None,
        offset=None,
        side=None,
        start=None,
        status=None,
        symbol=None,
        total=None,
    ):
        params = {
            "address": address,
            "end": end,
            "limit": limit,
            "offset": offset,
            "side": side,
            "start": start,
            "status": status,
            "symbol": symbol,
            "total": total,
        }
        return self.get_request("/orders/closed", params=params)

    async def get_open_orders(
        self, address, limit=None, offset=None, symbol=None, total=None
    ):
        prms = {
            "address": address,
            "limit": limit,
            "offset": offset,
            "symbol": symbol,
            "total": total,
        }
        return self.get_request("/orders/open", params=prms)

    async def get_orders_by_id(self, id):
        return self.get_request("/orders/" + id)

    async def get_ticker(self, symbol=None):
        prms = {"symbol": symbol}
        return self.get_request("/ticker/24hr", params=prms)

    async def get_trades(
        self,
        address=None,
        buyerOrderId=None,
        height=None,
        limit=None,
        offset=None,
        quoteAsset=None,
        sellerOrderId=None,
        side=None,
        start=None,
        end=None,
        total=None,
        symbol=None,
    ):
        prms = {
            "address": address,
            "buyerOrderId": buyerOrderId,
            "height": height,
            "limit": limit,
            "offset": offset,
            "sellerOrderId": sellerOrderId,
            "side": side,
            "start": start,
            "end": end,
            "symbol": symbol,
            "total": total,
        }
        return self.get_request("/trades", params=prms)

    async def get_transactions(
        self,
        address,
        blockHeight,
        startTime,
        endTime,
        limit,
        offset,
        side,
        txAsset,
        txType,
    ):
        prms = {
            "address": address,
            "blockHeight": blockHeight,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
            "offset": offset,
            "side": side,
            "txAsset": txAsset,
            "txType": txType,
        }


async def main():
    bnc = BNC("testnet-dex.binance.org")
    time = bnc.get_time()
    print(time)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
