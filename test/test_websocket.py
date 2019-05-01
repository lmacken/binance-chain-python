# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
Binance DEX WebSocket Test Suite
"""
import asyncio

import pytest

from binancechain import HTTPClient, WebSocket, Wallet, Transaction
from binancechain.enums import Timeinforce, Ordertype, Side


MNEMONIC = "tennis utility midnight pattern that foot security tent punch glance still night virus loop trade velvet rent glare ramp cushion defy grass section cage"


def on_error(msg):
    print(f'Error: {msg}')


async def perform_trade(symbols, httpclient, wallet):
    # Get the order book for the first symbol
    for symbol in symbols:
        if symbol.startswith('BNB_BTC'):
            break
    print(symbol)
    depth = await httpclient.get_depth(symbol)

    # Hit the bid
    bids = depth['bids']
    assert bids
    price = bids[0][0]

    address = wallet.get_address()
    transaction = await Transaction.new_order_transaction(
        address=address,
        symbol=symbol,
        side=Side.SELL,
        timeInForce=Timeinforce.IOC,
        price=price,
        quantity=1,
        ordertype=Ordertype.LIMIT,
        client=httpclient,
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await httpclient.broadcast(hex_data, sync=True)
    print(broadcast)

    # Hit the ask
    asks = depth['asks']
    assert asks
    price = asks[0][0]

    transaction = await Transaction.new_order_transaction(
        address=address,
        symbol=symbol,
        side=Side.BUY,
        timeInForce=Timeinforce.IOC,
        price=price,
        quantity=1,
        ordertype=Ordertype.LIMIT,
        client=httpclient,
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await httpclient.broadcast(hex_data, sync=True)
    print(broadcast)


@pytest.fixture
async def client():
    # If we create fresh websockets too fast it may error?
    await asyncio.sleep(1)
    client = WebSocket(testnet=True)
    yield client
    client.close()


@pytest.fixture
async def symbols():
    symbols = []
    rest = HTTPClient(testnet=True)
    markets = await rest.get_markets()
    for market in markets:
        symbol = f"{market['base_asset_symbol']}_{market['quote_asset_symbol']}"
        symbols.append(symbol)
    yield symbols
    await rest.close()


@pytest.fixture
async def httpclient():
    client = HTTPClient(testnet=True)
    yield client
    await client.close()


@pytest.fixture
async def wallet():
    wallet = Wallet.wallet_from_mnemonic(words=MNEMONIC, testnet=True)
    yield wallet


@pytest.mark.asyncio
async def test_open_close(client):
    """"Open then immediately close"""
    def on_open():
        print('opened')
        client.close()

    await client.start_async(on_open=on_open, on_error=on_error)
    print('closed')


@pytest.mark.asyncio
async def test_trades(client, symbols, httpclient, wallet):
    print(symbols)
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    async def on_open():
        client.subscribe_trades(symbols=symbols, callback=callback)
        await perform_trade(symbols, httpclient, wallet)

    await client.start_async(on_open=on_open, on_error=on_error)

    assert results
    result = results[0]
    assert result['stream'] == 'trades'


@pytest.mark.asyncio
async def test_market_diff(client, symbols, httpclient, wallet):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    async def on_open():
        client.subscribe_market_diff(symbols=symbols, callback=callback)
        await perform_trade(symbols, httpclient, wallet)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert result['stream'] == 'marketDiff'


@pytest.mark.asyncio
async def test_market_depth(client, symbols):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_market_depth(symbols=symbols, callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert result['stream'] == 'marketDepth'


@pytest.mark.asyncio
async def test_kline(client, symbols):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_kline(interval='1m', symbols=symbols, callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert result['stream'] == 'kline_1m'


@pytest.mark.asyncio
async def test_tickers(client, symbols):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_ticker(symbols=symbols, callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert result['stream'] == 'ticker'


@pytest.mark.asyncio
async def test_all_tickers(client):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_all_tickers(callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert result['stream'] == 'allTickers'


@pytest.mark.asyncio
async def test_mini_ticker(client, symbols):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_mini_ticker(symbols=symbols, callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert result['stream'] == 'miniTicker'


@pytest.mark.asyncio
async def test_all_mini_ticker(client, symbols):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_all_mini_tickers(callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert result['stream'] == 'allMiniTickers'


@pytest.mark.asyncio
async def test_blockheight(client):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_blockheight(callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert 'stream' in result


@pytest.mark.asyncio
async def test_keepalive(client):
    def on_open():
        client.keepalive()
        client.close()
    await client.start_async(on_open=on_open, on_error=on_error)


@pytest.mark.asyncio
async def test_unsubscribe(client):
    results = []

    def callback(msg):
        results.append(msg)
        client.unsubscribe("blockheight")
        client.close()

    def on_open():
        client.subscribe_blockheight(callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)
    assert results


@pytest.mark.asyncio
async def test_decorator(client):
    @client.on('open')
    def callback():
        client.close()
    await client.start_async()


@pytest.mark.asyncio
async def test_decorator_async(client):
    @client.on('open')
    async def callback():
        client.close()
    await client.start_async()


@pytest.mark.asyncio
async def test_decorator_sub_queue(client):
    results = []

    @client.on("allTickers", symbols=["$all"])
    async def callback(msg):
        results.append(msg)
        client.close()

    await client.start_async()
    assert results
