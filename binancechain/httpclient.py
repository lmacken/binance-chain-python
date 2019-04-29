# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
Binance Chain HTTP API

https://docs.binance.org/api-reference/dex-api/paths.html
"""
import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import orjson

from .exceptions import BinanceChainException
from .ratelimit import RateLimiter

log = logging.getLogger(__name__)

MAINNET_URL = "https://dex.binance.org"
TESTNET_URL = "https://testnet-dex.binance.org"


class HTTPClient:
    """ Binance Chain HTTP API Client """

    def __init__(
        self,
        testnet: bool = True,
        api_version: str = "v1",
        url=None,
        rate_limit: bool = False,
    ):
        """
        :param testnet: Use testnet instead of mainnet
        :param api_version: The API version to use
        :param session: An optional HTTP session to use
        :param rate_limit: Enable automatic rate-limiting
        """
        if not url:
            url = TESTNET_URL if testnet else MAINNET_URL
        self._server = f"{url}/api/{api_version}/"
        self._session: aiohttp.ClientSession = None
        self._testnet = testnet
        self._rate_limiter: Optional[RateLimiter] = None
        if rate_limit:
            self._rate_limiter = RateLimiter()

    def __del__(self):
        if self._session:  # pragma: nocover
            warnings.warn(f"{repr(self)}.close() was never awaited")

    async def close(self):
        """ Clean up our connections """
        if self._session:
            await self._session.close()
            self._session = None
        if self._rate_limiter:
            self._rate_limiter.close()

    async def _request(self, method: str, path: str, **kwargs):
        """
        :method: `get` or `post`
        :path: the remote endpoint to call
        :kwargs: Extra arguments to pass to the request, like `params` or `data`.
        :raises: `BinanceChainException`, which has a `response` attribute.
        """
        if not self._session:
            self._session = aiohttp.ClientSession()
        try:
            resp = None
            async with getattr(self._session, method)(
                self._server + path, **kwargs
            ) as resp:
                return await resp.json(loads=orjson.loads)
        except Exception as e:
            log.exception(f"Request error: {method} {path} {kwargs}")
            raise BinanceChainException(resp) from e

    async def get_request(self, path: str, params: dict = None) -> Any:
        """Perform a GET request"""
        return await self._request("get", path, params=params)

    async def post_request(
        self, path: str, data: Optional[str] = None, headers: Optional[dict] = None
    ) -> Any:
        """Perform a POST request"""
        return await self._request("post", path, data=data, headers=headers)

    async def get_time(self) -> dict:
        """Get the block time.

        Gets the latest block time and the current time according to the HTTP
        service.

        Destination: Validator node.
        Rate Limit: 1 request per IP per second.
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("time", 1)
        return await self.get_request("time")

    async def get_node_info(self) -> dict:
        """Get node information.

        Gets runtime information about the node.

        Destination: Validator node.
        Rate Limit: 1 request per IP per second.
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("node-info", 1)
        return await self.get_request("node-info")

    async def get_validators(self) -> dict:
        """Get validators.

        Gets the list of validators used in consensus.

        Destination: Witness node.
        Rate Limit: 10 requests per IP per second.
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("validators", 10)
        return await self.get_request("validators")

    async def get_peers(self) -> List[dict]:
        """Get network peers.

        Gets the list of network peers.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("peers", 1)
        return await self.get_request("peers")

    async def get_account(self, address: str) -> dict:
        """Get an account.

        Gets account metadata for an address.

        Destination: Witness node.
        Rate Limit: 5 requests per IP per second.

        :param address: The account address to query
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("account", 5)
        return await self.get_request(f"account/{address}")

    async def get_account_sequence(self, address: str) -> dict:
        """Get an account sequence.

        Gets an account sequence for an address.

        Destination: Validator node.
        Rate Limit: 5 requests per IP per second.
        Parameters:

        :param address: The account address to query.
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("account", 5)
        return await self.get_request(f"account/{address}/sequence")

    async def get_transaction(self, hash: str) -> dict:
        """Get a transaction.

        Gets transaction metadata by transaction ID. By default, transactions
        are returned in a raw format.

        Destination: Seed node.
        Rate Limit: 10 requests per IP per second.

        :param hash: The transaction hash to query
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("tx", 10)
        return await self.get_request(f"tx/{hash}")

    async def get_token_list(self) -> List[dict]:
        """Get tokens list.

        Gets a list of tokens that have been issued.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("tokens", 1)
        return await self.get_request("tokens")

    async def get_markets(self, limit: int = 500, offset: int = 0) -> List[dict]:
        """Get market pairs.

        Gets the list of market pairs that have been listed.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.

        :param limit: default 500; max 1000.
        :param offset: start with 0; default 0.
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("markets", 1)
        return await self.get_request(
            "markets", params={"limit": limit, "offset": offset}
        )

    async def get_fees(self) -> List[dict]:
        """Obtain trading fees information.

        Gets the current trading fees settings.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("fees", 1)
        return await self.get_request("fees")

    async def get_depth(self, symbol: str, limit: int = 100) -> Dict[str, list]:
        """Get the order book.

        Gets the order book depth data for a given pair symbol.
        The given limit must be one of the allowed limits below.

        Destination: Validator node.
        Rate Limit: 10 requests per IP per second.

        :param symbol: Market pair symbol, e.g. NNB-0AD_BNB
        :param limit: The limit of results. Allowed limits: [5, 10, 20, 50, 100, 500, 1000]
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("depth", 10)
        return await self.get_request(
            "depth", params={"symbol": symbol, "limit": limit}
        )

    async def broadcast(self, body: str, sync: bool = None) -> List[dict]:
        """Broadcast a transaction.

        Broadcasts a signed transaction. A single transaction must be sent
        hex-encoded with a content-type of text/plain.

        Destination: Witness node.
        Rate Limit: 5 requests per IP per second.

        :param sync: Synchronous broadcast (wait for DeliverTx)?
        :param body: Hex-encoded transaction
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("broadcast", 5)
        return await self.post_request(
            "broadcast", data=body, headers={"Content-Type": "text/plain"}
        )

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 300,
        start: int = None,
        end: int = None,
    ) -> List[Tuple[int, str, str, str, str, str, int, str, int]]:
        """Get candlestick bars.

        Gets candlestick/kline bars for a symbol. Bars are uniquely identified
        by their open time.

        If the time window is larger than limits, only the first n klines will
        return. In this case, please either shrink the window or increase the
        limit to get proper amount of klines.

        Rate Limit: 10 requests per IP per second.

        :param symbol: symbol
        :param interval: interval. Allowed value: [1m, 3m, 5m, 15m, 30m, 1h,
            2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M]
        :param limit: default 300; max 1000.
        :param start: start time in Milliseconds
        :param end: end time in Milliseconds
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("klines", 10)
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start is not None:
            params["startTime"] = int(start)
        if end is not None:
            params["endTime"] = int(end)
        return await self.get_request("klines", params=params)

    async def get_closed_orders(
        self,
        address: str,
        end: int = None,
        limit: int = None,
        offset: int = None,
        side: int = None,
        start: int = None,
        status: str = None,
        symbol: str = None,
        total: int = None,
    ) -> List[dict]:
        """Get closed orders.

        Gets closed (filled and cancelled) orders for a given address.

        Query Window: Default query window is latest 7 days; The maximum
        start - end query window is 3 months.
        Rate Limit: 5 requests per IP per second.

        :param address: the owner address
        :param end: end time in Milliseconds
        :param limit: default 500; max 1000.
        :param offset: start with 0; default 0.
        :param side: order side. 1 for buy and 2 for sell.
        :param start: start time in Milliseconds
        :param status: order status list. Allowed value: [Ack, PartialFill,
            IocNoFill, FullyFill, Canceled, Expired, FailedBlocking,
            FailedMatching]
        :param symbol: symbol
        :param total: total number required, 0 for not required and 1 for
            required; default not required, return total=-1 in response
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("orders", 5)
        params = {"address": address}
        if end is not None:
            params["end"] = int(end)
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if side is not None:
            params["side"] = side
        if start is not None:
            params["start"] = int(start)
        if status is not None:
            params["status"] = status
        if symbol is not None:
            params["symbol"] = symbol
        if total is not None:
            params["total"] = total
        return await self.get_request("orders/closed", params=params)

    async def get_open_orders(
        self,
        address: str,
        limit: int = None,
        offset: int = None,
        symbol: str = None,
        total: int = None,
    ):
        """Get open orders.

        Gets open orders for a given address.

        Rate Limit: 5 requests per IP per second.

        :param address: the owner address
        :param limit: default 500; max 1000.
        :param offset: start with 0; default 0.
        :param symbol: symbol
        :param total: total number required, 0 for not required and 1 for
            required; default not required, return total=-1 in response
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("orders", 5)
        params = {"address": address}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if symbol is not None:
            params["symbol"] = symbol
        if total is not None:
            params["total"] = total
        return await self.get_request("orders/open", params=params)

    async def get_order(self, id: str) -> dict:
        """Get an order.

        Gets metadata for an individual order by its ID.

        Rate Limit: 5 requests per IP per second.

        :param id: order id
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("orders", 5)
        return await self.get_request(f"orders/{id}")

    async def get_ticker(self, symbol: str = None) -> List[dict]:
        """Get a market ticker.

        Gets 24 hour price change statistics for a market pair symbol.

        Rate Limit: 5 requests per IP per second.

        :param symbol: symbol
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("ticker", 5)
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self.get_request("ticker/24hr", params=params)

    async def get_trades(
        self,
        address: str = None,
        buyerOrderId: str = None,
        height: int = None,
        limit: int = None,
        offset: int = None,
        quoteAsset: str = None,
        sellerOrderId: str = None,
        side: int = None,
        start: int = None,
        end: int = None,
        total: int = None,
        symbol: str = None,
    ) -> List[dict]:
        """Get market trades.

        Gets a list of historical trades.

        Query Window: Default query window is latest 7 days; The maximum
        start - end query window is 3 months.

        Rate Limit: 5 requests per IP per second.

        :param address: the buyer/seller address
        :param buyerOrderId: buyer order id
        :param end: end time in Milliseconds
        :param height: block height
        :param limit: default 500; max 1000.
        :param start: start with 0; default 0.
        :param quoteAsset: quote asset
        :param sellerOrderId: seller order id
        :param side: order side. 1 for buy and 2 for sell.
        :param start: start time in Milliseconds
        :param symbol: symbol
        :param total: total number required, 0 for not required and 1 for
            required; default not required, return total=-1 in response
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("trades", 5)
        params: Dict[Any, Any] = {}
        if address is not None:
            params["address"] = address
        if buyerOrderId is not None:
            params["buyerOrderId"] = buyerOrderId
        if height is not None:
            params["height"] = height
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sellerOrderId is not None:
            params["sellerOrderId"] = sellerOrderId
        if side is not None:
            params["side"] = side
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if symbol is not None:
            params["symbol"] = symbol
        if total is not None:
            params["total"] = total
        return await self.get_request("trades", params=params)

    async def get_block_exchange_fee(
        self,
        address: str = None,
        end: int = None,
        limit: int = None,
        offset: int = None,
        start: int = None,
        total: int = None,
    ) -> List[dict]:
        """Trading fee of the address grouped by block

        Get historical trading fees of the address, including fees of
        trade/canceled order/expired order. Transfer and other transaction fees
        are not included. Order by block height DESC.

        Query Window: Default query window is latest 7 days; The maximum
        start - end query window is 3 months.

        Rate Limit: 5 requests per IP per second.

        :param address: the buyer/seller address
        :param buyerOrderId: buyer order id
        :param end: end time in Milliseconds
        :param limit: default 500; max 1000.
        :param offset: start with 0; default 0.
        :param start: start with 0; default 0.
        :param total: total number required, 0 for not required and 1 for
            required; default not required, return total=-1 in response
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("block-exchange-fee", 5)
        params: Dict[Any, Any] = {}
        if address is not None:
            params["address"] = address
        if end is not None:
            params["end"] = end
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if start is not None:
            params["start"] = start
        if total is not None:
            params["total"] = total
        return await self.get_request("block-exchange-fee", params=params)

    async def get_transactions(
        self,
        address: str,
        height: int = None,
        end: int = None,
        limit: int = None,
        offset: int = None,
        side: str = None,
        start: int = None,
        tx_asset: str = None,
        tx_type: str = None,
    ) -> List[dict]:
        """Get transactions.

        Gets a list of transactions. Multisend transaction is not available in
        this API.

        Query Window: Default query window is latest 24 hours; The maximum
        start - end query window is 3 months.

        Rate Limit: 60 requests per IP per minute.

        :param address: address
        :param height: block height
        :param end: end time in milliseconds
        :param limit: limit
        :param offset: offset
        :param side: transaction side. Allowed value: [ RECEIVE, SEND]
        :param start: start time in milliseconds
        :param tx_asset: txAsset
        :param tx_type: transaction type. Allowed value: [
            NEW_ORDER,ISSUE_TOKEN,BURN_TOKEN,LIST_TOKEN,CANCEL_ORDER,FREEZE_TOKEN,
            UN_FREEZE_TOKEN,TRANSFER,PROPOSAL,VOTE,MINT,DEPOSIT]
        """
        if self._rate_limiter:
            await self._rate_limiter.limit("transactions", 1)
        params: Dict[Any, Any] = {"address": address}
        if height is not None:
            params["blockHeight"] = height
        if start is not None:
            params["startTime"] = start
        if end is not None:
            params["endTime"] = end
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if side is not None:
            params["side"] = side
        if tx_asset is not None:
            params["txAsset"] = tx_asset
        if tx_type is not None:
            params["txType"] = tx_type
        return await self.get_request("transactions", params=params)
