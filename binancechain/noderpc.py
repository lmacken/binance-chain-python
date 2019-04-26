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
Binance Chain Node RPC HTTP API

https://docs.binance.org/api-reference/node-rpc.html#node-rpc

Endpoints that require arguments:

/subscribe?query=_
/unsubscribe?query=_
/unsubscribe_all?
"""
import itertools
import sys
import traceback
import warnings
from typing import Any, Dict, List, Optional

import aiohttp

from .exceptions import BinanceChainException

MAINNET_URL = ""
# TODO: get this dynamically?
TESTNET_URL = "https://seed-pre-s3.binance.org/"


class BinanceChainNodeRPC:
    """ Binance Chain Node RPC HTTP API Client """

    def __init__(self, url: str = None, testnet: bool = True):
        """
        :param testnet: A boolean to enable testnet
        :param session: An optional HTTP session to use
        """
        if not url:
            self.url = TESTNET_URL if testnet else MAINNET_URL
        self._id = itertools.count()
        self._session: aiohttp.ClientSession = None

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
        print(method, path, kwargs)
        if not self._session:
            self._session = aiohttp.ClientSession()
        try:
            resp = None
            async with getattr(self._session, method)(
                self.url + path, **kwargs
            ) as resp:
                return await resp.json()
        except Exception as e:
            raise BinanceChainException(resp) from e

    async def get_request(self, path: str, params: dict = None) -> Any:
        return await self._request("get", path, params=params)

    async def post_request(self, method: str, *params) -> dict:
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": str(next(self._id)),
        }
        if not self._session:
            self._session = aiohttp.ClientSession()
        try:
            async with self._session.post(self.url, json=payload) as resp:
                return await resp.json()
        except Exception as e:
            raise BinanceChainException(resp) from e

    async def get_abci_info(self) -> dict:
        """Get some info about the application."""
        return await self.get_request("abci_info")

    async def get_consensus_state(self) -> dict:
        """ConsensusState returns a concise summary of the consensus state.
        This is just a snapshot of consensus state, and it will not persist.
        """
        return await self.get_request("consensus_state")

    async def get_dump_consensus_state(self) -> dict:
        """ConsensusState returns a concise summary of the consensus state.
        This is just a snapshot of consensus state, and it will not persist.
        """
        return await self.get_request("dump_consensus_state")

    async def get_genesis(self) -> dict:
        """Get genesis file."""
        return await self.get_request("genesis")

    async def get_health(self) -> dict:
        """Get node health.
        Returns empty result on success, no response - in case of an error.
        """
        return await self.get_request("health")

    async def get_net_info(self) -> dict:
        """Get network info."""
        return await self.get_request("net_info")

    async def get_num_unconfirmed_txs(self) -> dict:
        """Get number of unconfirmed transactions."""
        return await self.get_request("num_unconfirmed_txs")

    async def get_status(self) -> dict:
        """Get Tendermint status including node info, pubkey, latest block
        hash, app hash, block height and time.
        """
        return await self.get_request("status")

    async def abci_query(
        self, path: str, data: str = None, height: str = "0", prove: bool = False
    ) -> dict:
        """Query the application for some information.

        Available Query Paths:

            /store/acc/key
            /tokens/info
            /tokens/list
            /dex/pairs
            /dex/orderbook
            /param/fees
        """
        return await self.post_request("abci_query", path, data, height, prove)

    async def block(self, height: Optional[int] = None) -> dict:
        """Query the block at a given height.

        :param height: height of blockchain
        """
        return await self.post_request("block", height)

    async def block_by_hash(self, hash: str) -> dict:
        """Query a block by it's hash.
        :param hash: the block hash
        """
        return await self.post_request("block_by_hash", hash)

    async def block_results(self, height: Optional[str] = None) -> dict:
        """Gets ABCIResults at a given height."""
        return await self.post_request("block_results", height)

    async def blockchain(self, min_height: str, max_height: str) -> dict:
        """Get block headers for minHeight <= height <= maxHeight.
        Block headers are returned in descending order (highest first).
        """
        return await self.post_request("blockchain", min_height, max_height)

    async def broadcast_tx_async(self, tx: str) -> dict:
        """
        This method just returns the transaction hash right away and there is no
        return from CheckTx or DeliverTx.
        """
        return await self.post_request("broadcast_tx_async", tx)

    async def broadcast_tx_sync(self, tx: str) -> dict:
        """
        The transaction will be broadcasted and returns with the response from CheckTx.
        """
        return await self.post_request("broadcast_tx_sync", tx)

    async def broadcast_tx_commit(self, tx: str) -> dict:
        """
        The transaction will be broadcasted and returns with the response from
        CheckTx and DeliverTx.

        If CheckTx or DeliverTx fail, no error will be returned, but the
        returned result will contain a non-OK ABCI code.
        """
        return await self.post_request("broadcast_tx_commit", tx)

    async def commit(self, height: Optional[str] = None) -> dict:
        """Get block commit at a given height.
        If no height is provided, it will fetch the commit for the latest block.
        """
        return await self.post_request("commit", height)

    async def consensus_params(self, height: Optional[str] = None) -> dict:
        """Get consensus params at a given height."""
        return await self.post_request("consensus_params", height)

    async def tx(self, hash: str, prove: bool = False) -> dict:
        """Allows you to query the transaction results."""
        return await self.post_request("tx", hash, prove)

    async def tx_search(
        self, query: str, prove: bool = False, page: int = 1, per_page: int = 30
    ) -> dict:
        """Allows you to query for multiple transactions results.
        You could search transaction by its index. It returns a list of
        transactions (maximum ?per_page entries) and the total count.
        """
        return await self.post_request(
            "tx_search", query, prove, str(page), str(per_page)
        )

    async def unconfirmed_txs(self, limit: int = None) -> dict:
        """Get unconfirmed transactions."""
        return await self.post_request("unconfirmed_txs", limit)

    async def validators(self, height: str = None) -> dict:
        """Get information on the validators"""
        return await self.post_request("validators", height)
