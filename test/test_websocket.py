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
Binance DEX WebSocket Test Suite
"""
import asyncio

import pytest

from binancechain import BinanceChain, BinanceChainWebSocket


def on_error(msg):
    print(f'Error: {msg}')


@pytest.fixture
async def client():
    # If we create fresh websockets too fast it may error?
    await asyncio.sleep(1)
    client = BinanceChainWebSocket(testnet=True)
    yield client
    client.close()


@pytest.fixture
async def symbols():
    symbols = []
    rest = BinanceChain(testnet=True)
    markets = await rest.get_markets()
    for market in markets:
        symbol = f"{market['base_asset_symbol']}_{market['quote_asset_symbol']}"
        symbols.append(symbol)
    yield symbols
    await rest.close()


@pytest.mark.asyncio
async def test_open_close(client):
    """"Open then immediately close"""
    def on_open():
        print('opened')
        client.close()

    await client.start_async(on_open=on_open, on_error=on_error)
    print('closed')


@pytest.mark.asyncio
async def test_trades(client, symbols):
    print(symbols)
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_trades(symbols=symbols, callback=callback)

    await client.start_async(on_open=on_open, on_error=on_error)

    result = results[0]
    assert result['stream'] == 'trades'


@pytest.mark.asyncio
async def test_market_diff(client, symbols):
    results = []

    def callback(msg):
        results.append(msg)
        client.close()

    def on_open():
        client.subscribe_market_diff(symbols=symbols, callback=callback)

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
