# Copyright 2019 Sensei.Chat
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# SPDX-License-Identifier: MIT
"""
Binance Chain HTTP API

https://docs.binance.org/api-reference/dex-api/paths.html
"""
import sys
import traceback
import warnings
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

MAINNET_URL = ""
TESTNET_URL = "https://testnet-dex.binance.org"


class BinanceChain:
    """ Binance Chain HTTP API Client """

    def __init__(self, testnet: bool = True, api_version: str = "v1"):
        """
        :param testnet: A boolean to enable testnet
        :param api_version: The API version to use
        :param session: An optional HTTP session to use
        """
        url = TESTNET_URL if testnet else MAINNET_URL
        self._server = f"{url}/api/{api_version}/"
        self._session: aiohttp.ClientSession = None

    def __del__(self):
        if self._session:  # pragma: nocover
            warnings.warn(f"{repr(self)}.close() was never awaited")

    async def close(self):
        """ Clean up our connections """
        if self._session:
            try:
                await self._session.close()
                self._session = None
            except Exception as e:  # pragma: nocover
                traceback.print_exc()

    async def _request(self, method: str, path: str, **kwargs):
        """
        :method: `get` or `post`
        :path: the remote endpoint to call
        :kwargs: Extra arguments to pass to the request, like `params` or `data`.
        """
        print(method, path, kwargs)
        if not self._session:
            self._session = aiohttp.ClientSession()
        try:
            resp = None
            async with getattr(self._session, method)(
                self._server + path, **kwargs
            ) as resp:
                return await resp.json()
        except Exception as e:
            if resp:
                text = await resp.text()
                if not text:
                    print(f"Empty response from `{path}`", file=sys.stderr)
                else:  # pragma: nocover
                    print(f"Error: {text}", file=sys.stderr)
            else:
                raise

    async def get_request(self, path: str, params: dict = None) -> Any:
        return await self._request("get", path, params=params)

    async def post_request(
        self, path: str, data: Optional[str] = None, headers: Optional[dict] = None
    ) -> Any:
        return await self._request("post", path, data=data, headers=headers)

    async def get_time(self) -> dict:
        """Get the block time.

        Gets the latest block time and the current time according to the HTTP
        service.

        Destination: Validator node.
        Rate Limit: 1 request per IP per second.
        """
        return await self.get_request("time")

    async def get_node_info(self) -> dict:
        """Get node information.

        Gets runtime information about the node.

        Destination: Validator node.
        Rate Limit: 1 request per IP per second.
        """
        return await self.get_request("node-info")

    async def get_validators(self) -> dict:
        """Get validators.

        Gets the list of validators used in consensus.

        Destination: Witness node.
        Rate Limit: 10 requests per IP per second.
        """
        return await self.get_request("validators")

    async def get_peers(self) -> List[dict]:
        """Get network peers.

        Gets the list of network peers.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.
        """
        return await self.get_request("peers")

    async def get_account(self, address: str) -> dict:
        """Get an account.

        Gets account metadata for an address.

        Destination: Witness node.
        Rate Limit: 5 requests per IP per second.

        :param address: The account address to query
        """
        return await self.get_request(f"account/{address}")

    async def get_account_sequence(self, address: str) -> dict:
        """Get an account sequence.

        Gets an account sequence for an address.

        Destination: Validator node.
        Rate Limit: 5 requests per IP per second.
        Parameters:

        :param address: The account address to query.
        """
        return await self.get_request(f"account/{address}/sequence")

    async def get_transaction(self, hash: str) -> dict:
        """Get a transaction.

        Gets transaction metadata by transaction ID. By default, transactions
        are returned in a raw format.

        Destination: Seed node.
        Rate Limit: 10 requests per IP per second.

        :param hash: The transaction hash to query
        """
        return await self.get_request(f"tx/{hash}")

    async def get_token_list(self) -> List[dict]:
        """Get tokens list.

        Gets a list of tokens that have been issued.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.
        """
        return await self.get_request("tokens")

    async def get_markets(self, limit: int = 500, offset: int = 0) -> List[dict]:
        """Get market pairs.

        Gets the list of market pairs that have been listed.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.

        :param limit: default 500; max 1000.
        :param offset: start with 0; default 0.
        """
        return await self.get_request(
            "markets", params={"limit": limit, "offset": offset}
        )

    async def get_fees(self) -> List[dict]:
        """Obtain trading fees information.

        Gets the current trading fees settings.

        Destination: Witness node.
        Rate Limit: 1 request per IP per second.
        """
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
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start:
            params["startTime"] = start
        if end:
            params["endTime"] = end
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
        params = {
            "address": address,
        }
        if end:
            params['end'] = end
        if limit:
            params["limit"] = limit
        if offset:
            params['offset'] = offset
        if side:
            params['side'] = side
        if start:
            params['start'] = start
        if status:
            params['status'] = status
        if symbol:
            params['symbol'] = symbol
        if total:
            params['total'] = total
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
        params = {"address": address}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if symbol:
            params["symbol"] = symbol
        if total:
            params["total"] = total
        return await self.get_request("orders/open", params=params)

    async def get_order(self, id: str) -> dict:
        """Get an order.

        Gets metadata for an individual order by its ID.

        Rate Limit: 5 requests per IP per second.

        :param id: order id
        """
        return await self.get_request(f"orders/{id}")

    async def get_ticker(self, symbol: str = None) -> List[dict]:
        """Get a market ticker.

        Gets 24 hour price change statistics for a market pair symbol.

        Rate Limit: 5 requests per IP per second.

        :param symbol: symbol
        """
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
        params: Dict[Any, Any] = {}
        if address:
            params["address"] = address
        if buyerOrderId:
            params["buyerOrderId"] = buyerOrderId
        if height:
            params["height"] = height
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if sellerOrderId:
            params["sellerOrderId"] = sellerOrderId
        if side:
            params["side"] = side
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if symbol:
            params["symbol"] = symbol
        if total:
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
        params: Dict[Any, Any] = {}
        if address:
            params["address"] = address
        if end:
            params["end"] = end
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if start:
            params["start"] = start
        if total:
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
        params: Dict[Any, Any] = {"address": address}
        if height:
            params["blockHeight"] = height
        if start:
            params["startTime"] = start
        if end:
            params["endTime"] = end
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if side:
            params["side"] = side
        if tx_asset:
            params["txAsset"] = tx_asset
        if tx_type:
            params["txType"] = tx_type
        return await self.get_request("transactions", params=params)
