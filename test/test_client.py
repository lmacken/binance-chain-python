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
            "base_asset_symbol",
            "list_price",
            "lot_size",
            "quote_asset_symbol",
            "tick_size",
        ):
            assert key in market


@pytest.mark.asyncio
async def test_get_fees(client):
    fees = await client.get_fees()
    pprint(fees)
    # for fee in fees:
    # for key in ("fee_for",):
    #   assert key in fee, fee


"""
TODO: actual testnet tx stuff

@pytest.mark.asyncio
async def test_get_transaction(client):
    h = "E81BAB8E555819E4211D62E2E536B6D5812D3D91C105F998F5C6EB3AB8136482"
    tx = await client.get_transaction(h)
    pprint(tx)
    assert False
    for key in ("fee", "fee_for", "msg_type"):
        assert key in tx


@pytest.mark.asyncio
async def test_broadcast(client):
    body = ...
    tx = await client.broadcast(body)
    pprint(tx)

@pytest.mark.asyncio
async def test_get_closed_orders(client):
    address = ...
    orders = await client.get_closed_orders(address)
    pprint(order)
    assert False
    #for kline in klines:
    #    assert len(kline) == 9

@pytest.mark.asyncio
async def test_get_open_orders(client):
    address = ...
    orders = await client.get_open_orders(address)
    pprint(order)
    assert False
    #for kline in klines:
    #    assert len(kline) == 9

@pytest.mark.asyncio
async def test_get_order(client):
    id = ...
    orders = await client.get_order(id)
    pprint(order)
    assert False
"""


@pytest.mark.asyncio
async def test_get_klines(client):
    markets = await client.get_markets()
    market = markets[0]
    symbol = "{base_asset_symbol}_{quote_asset_symbol}".format_map(market)
    interval = "4h"
    pprint(market)
    klines = await client.get_klines(symbol=symbol, interval=interval)
    pprint(klines)
    for kline in klines:
        assert len(kline) == 9


@pytest.mark.asyncio
async def test_get_ticker(client):
    tickers = await client.get_ticker()
    pprint(tickers)
    for ticker in tickers:
        for key in ("askPrice", "askQuantity", "bidPrice", "bidQuantity"):
            assert key in ticker


@pytest.mark.asyncio
async def test_trades(client):
    trades = await client.get_trades()
    pprint(trades)
    assert 'total' in trades
    assert 'trade' in trades
    for trade in trades['trade']:
        for key in (
            "baseAsset",
            "blockHeight",
            "buyFee",
            "buyerId",
            "buyerOrderId",
            "price",
            "quantity",
            "quoteAsset",
            "sellFee",
            "sellerId",
            "sellerOrderId",
            "symbol",
            "time",
            "tradeId",
        ):
            assert key in trade
