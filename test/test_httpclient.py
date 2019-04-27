# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
Binance DEX SDK Test Suite
"""
from pprint import pprint
from datetime import datetime, timedelta

import aiohttp
import pytest

from binancechain import HTTPClient, BinanceChainException


@pytest.fixture
async def client():
    client = HTTPClient(testnet=True)
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
    assert fees
    assert "fee" in fees[0]


@pytest.mark.asyncio
async def test_get_transaction(client):
    h = "F9016F01A1098BF8024C28C8400AE010FC32DC8A393ADB26E56F37BC8B0C5D66"
    tx = await client.get_transaction(h)
    for key in ("ok", "log", "hash", "data"):
        assert key in tx
    assert tx["ok"]


@pytest.mark.asyncio
async def test_get_account(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    account = await client.get_account(address)
    assert "address" in account


@pytest.mark.asyncio
async def test_get_account_sequence(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    account = await client.get_account_sequence(address)
    assert "sequence" in account


@pytest.mark.asyncio
async def test_get_closed_orders(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    orders = await client.get_closed_orders(address, limit=1)
    assert "order" in orders

    start = (datetime.utcnow() - timedelta(days=1)).timestamp()
    end = datetime.utcnow().timestamp()
    markets = await client.get_markets()
    market = markets[0]
    symbol = "{base_asset_symbol}_{quote_asset_symbol}".format_map(market)
    orders = await client.get_closed_orders(
        address,
        start=start,
        end=end,
        offset=1,
        side=1,
        status="Ack",
        symbol=symbol,
        total=1,
    )
    assert "order" in orders


@pytest.mark.asyncio
async def test_get_open_orders(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    markets = await client.get_markets()
    market = markets[0]
    symbol = "{base_asset_symbol}_{quote_asset_symbol}".format_map(market)
    orders = await client.get_open_orders(
        address, limit=1, offset=0, total=1, symbol=symbol
    )
    pprint(orders)
    assert "order" in orders


@pytest.mark.asyncio
async def test_get_transactions(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    transactions = await client.get_transactions(address=address)
    assert "tx" in transactions

    transactions = await client.get_transactions(
        address=address,
        height=999,
        start=11,
        end=999999,
        limit=1,
        offset=0,
        side="RECEIVE",
        tx_asset="test",
        tx_type="NEW_ORDER",
    )
    assert "tx" in transactions


@pytest.mark.asyncio
async def test_get_order(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    orders = await client.get_closed_orders(address)
    closed_order = orders["order"][0]
    order_id = closed_order["orderId"]
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
    interval = "1m"
    pprint(market)
    start = (datetime.utcnow() - timedelta(days=7)).timestamp()
    end = datetime.utcnow().timestamp()
    klines = await client.get_klines(
        symbol=symbol, interval=interval, start=start, end=end
    )
    pprint(klines)
    for kline in klines:
        assert len(kline) == 9


@pytest.mark.asyncio
async def test_get_ticker(client):
    tickers = await client.get_ticker()
    pprint(tickers)
    assert tickers
    for ticker in tickers:
        for key in ("askPrice", "askQuantity", "bidPrice", "bidQuantity"):
            assert key in ticker

    markets = await client.get_markets()
    market = markets[0]
    symbol = f"{market['base_asset_symbol']}_{market['quote_asset_symbol']}"
    tickers = await client.get_ticker(symbol=symbol)
    assert tickers
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
async def test_get_trades_for_address(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    trades = await client.get_trades(address=address)
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
async def test_get_trades_other_params(client):
    trades = await client.get_trades(
        buyerOrderId="abc",
        height=999999,
        limit=1,
        offset=0,
        sellerOrderId="zyx",
        side=1,
        start=0,
        end=99999999,
        total=1,
        symbol="xyz",
    )
    assert trades


@pytest.mark.asyncio
async def test_get_block_exchange_fee(client):
    address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"
    fees = await client.get_block_exchange_fee(address)
    assert "blockExchangeFee" in fees
    fees = await client.get_block_exchange_fee(
        address, start=111111, end=99999999, offset=0, limit=1, total=1
    )
    assert "blockExchangeFee" in fees


@pytest.mark.asyncio
async def test_get_depth(client):
    markets = await client.get_markets()
    market = markets[0]
    symbol = f"{market['base_asset_symbol']}_{market['quote_asset_symbol']}"
    depth = await client.get_depth(symbol)
    assert "asks" in depth and "bids" in depth


@pytest.mark.asyncio
async def test_invalid_request(client):
    client._server = "https://binance.com/"
    try:
        resp = await client.post_request("INVALID")
        assert False, resp
    except BinanceChainException as e:
        assert e.response.status == 404
        assert isinstance(e.__cause__, aiohttp.ContentTypeError)


@pytest.mark.asyncio
async def test_del_without_close_warning():
    client = HTTPClient(testnet=True)
    await client.get_time()
    with pytest.warns(UserWarning):
        del (client)
