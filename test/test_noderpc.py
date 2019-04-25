# Copyright 2019 Sensei.Chat <https://sensei.chat>
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
Binance Chain Node RPC Test Suite
"""
import pytest
from binancechain import BinanceChainNodeRPC


@pytest.fixture
async def noderpc():
    noderpc = BinanceChainNodeRPC(testnet=True)
    yield noderpc
    await noderpc.close()


@pytest.mark.asyncio
async def test_abci_info(noderpc):
    resp = await noderpc.get_abci_info()
    assert 'result' in resp


@pytest.mark.asyncio
async def test_consensus_state(noderpc):
    resp = await noderpc.get_consensus_state()
    assert 'result' in resp


@pytest.mark.asyncio
async def test_get_dump_consensus_state(noderpc):
    resp = await noderpc.get_dump_consensus_state()
    assert 'result' in resp


@pytest.mark.asyncio
async def test_get_genesis(noderpc):
    resp = await noderpc.get_genesis()
    assert 'result' in resp


@pytest.mark.asyncio
async def test_get_health(noderpc):
    resp = await noderpc.get_health()
    assert 'result' in resp


@pytest.mark.asyncio
async def test_net_info(noderpc):
    resp = await noderpc.get_net_info()
    assert 'result' in resp


@pytest.mark.asyncio
async def test_get_num_unconfirmed_txs(noderpc):
    resp = await noderpc.get_num_unconfirmed_txs()
    assert 'result' in resp


@pytest.mark.asyncio
async def test_get_status(noderpc):
    resp = await noderpc.get_status()
    assert 'result' in resp
