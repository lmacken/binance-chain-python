# Copyright 2019 Sensei.Chat
# # Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
"""
Binance DEX SDK Test Suite
"""
from pprint import pprint

import pytest

from binancedex.httpclient import BNC


@pytest.fixture
async def client():
    client = BNC(testnet=True)
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_time(client):
    time = await client.get_time()
    pprint(time)
    for key in ("ap_time", "block_time"):
        assert key in time


@pytest.mark.asyncio
async def test_node_info(client):
    info = await client.get_node_info()
    pprint(info)
    for key in ("node_info", "sync_info", "validator_info"):
        assert key in info


@pytest.mark.asyncio
async def test_get_validators(client):
    validators = await client.get_validators()
    pprint(validators)
    for key in ("block_height", "validators"):
        assert key in validators


@pytest.mark.asyncio
async def test_get_peers(client):
    peers = await client.get_peers()
    pprint(peers)
    assert isinstance(peers, list)
    assert len(peers)
    for peer in peers:
        for key in ("version", "network", "moniker", "id", "capabilities"):
            assert key in peer


# TODO:
# get_transaction(txid)


@pytest.mark.asyncio
async def test_token_list(client):
    tokens = await client.get_token_list()
    pprint(tokens)
    for token in tokens:
        for key in (
            "mintable",
            "name",
            "original_symbol",
            "owner",
            "symbol",
            "total_supply",
        ):
            assert key in token


@pytest.mark.asyncio
async def test_get_markets(client):
    markets = await client.get_markets()
    pprint(markets)
    for market in markets:
        for key in (
            "mintable",
            "name",
            "original_symbol",
            "owner",
            "symbol",
            "total_supply",
        ):
            assert key in market


@pytest.mark.asyncio
async def test_get_fees(client):
    fees = await client.get_fees()
    pprint(fees)
    for fee in fees:
        for key in ("fee", "fee_for", "msg_type"):
            assert key in fee
