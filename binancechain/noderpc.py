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


Available endpoints that don't require arguments:

/num_unconfirmed_txs
/status

Endpoints that require arguments:

/abci_query?path=_&data=_&prove=_
/block?height=_
/block_result?height=_
/blockchain?minHeight=_&maxHeight=_
/broadcast_tx_async?tx=_
/broadcast_tx_commit?tx=_
/broadcast_tx_sync?tx=_
/commit?height=_
/consensus_params?height=_
/dial_seeds?seeds=_
/dial_persistent_peers?persistent_peers=_
/subscribe?query=_
/tx?hash=_&prove=_
/tx_search?query=_&prove=_&page=_&per_page=_
/unconfirmed_txs?limit=_
/unsubscribe?query=_
/unsubscribe_all?
/validators?height=_
"""
import sys
import traceback
import warnings
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

MAINNET_URL = ""
# TODO: get this dynamically?
TESTNET_URL = "https://seed-pre-s3.binance.org/"


class BinanceChainNodeRPC:
    """ Binance Chain Node RPC HTTP API Client """

    def __init__(
        self,
        url: str = None,
        testnet: bool = True,
        session: aiohttp.ClientSession = None,
    ):
        """
        :param testnet: A boolean to enable testnet
        :param session: An optional HTTP session to use
        """
        if not url:
            self.url = TESTNET_URL if testnet else MAINNET_URL
        self._session = session or aiohttp.ClientSession()

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
        try:
            resp = None
            async with getattr(self._session, method)(
                self.url + path, **kwargs
            ) as resp:
                data = None
                try:
                    data = await resp.json()
                except Exception as e:
                    print(f"Error: Unable to parse JSON: {resp}", file=sys.stderr)
                    return resp
                return data
        except Exception as e:
            if resp:
                text = await resp.text()
                if not text:
                    print(f"Empty response from `{path}`", file=sys.stderr)
                else:
                    print(f"Error: {text}", file=sys.stderr)
            else:
                raise

    async def get_request(self, path: str, params: dict = None) -> Any:
        return await self._request("get", path, params=params)

    async def post_request(
        self, path: str, data: Optional[str] = None, headers: Optional[dict] = None
    ) -> Any:
        return await self._request("post", path, data=data, headers=headers)

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
