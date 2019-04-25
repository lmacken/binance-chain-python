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
Binance DEX SDK Test Suite
"""
from pprint import pprint

import pytest
from binancechain import BinanceChain


@pytest.fixture
async def client():
    client = BinanceChain(testnet=True)
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


@pytest.mark.asyncio
async def test_get_transaction(client):
    h = "F9016F01A1098BF8024C28C8400AE010FC32DC8A393ADB26E56F37BC8B0C5D66"
    tx = await client.get_transaction(h)
    for key in ("ok", "log", "hash", "data"):
        assert key in tx
    assert tx['ok']


@pytest.mark.asyncio
async def test_get_closed_orders(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    orders = await client.get_closed_orders(address)
    assert 'order' in orders


@pytest.mark.asyncio
async def test_get_open_orders(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    orders = await client.get_open_orders(address)
    pprint(orders)
    assert 'order' in orders


@pytest.mark.asyncio
async def test_get_transactions(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    transactions = await client.get_transactions(address=address)
    assert 'tx' in transactions


@pytest.mark.asyncio
async def test_get_order(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    orders = await client.get_closed_orders(address)
    closed_order = orders['order'][0]
    order_id = closed_order['orderId']
    order = await client.get_order(order_id)
    assert order == closed_order

"""
@pytest.mark.asyncio
async def test_broadcast(client):
    body = ...
    tx = await client.broadcast(body)
    pprint(tx)

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
    assert "total" in trades
    assert "trade" in trades
    for trade in trades["trade"]:
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


@pytest.mark.asyncio
async def test_get_block_exchange_fee(client):
    fees = await client.get_block_exchange_fee()
    pprint(fees)
    # TODO: returns None w/o an address
    # assert False
    # for fee in fees:
    #    for key in ("askPrice", "askQuantity", "bidPrice", "bidQuantity"):
    #        assert key in ticker
