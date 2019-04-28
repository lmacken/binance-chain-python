# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
Binance Chain Node RPC Test Suite
"""
import pytest
import aiohttp

from binancechain import NodeRPC, BinanceChainException


@pytest.fixture
async def noderpc():
    noderpc = NodeRPC(testnet=True)
    yield noderpc
    noderpc.close()


def on_error(msg):
    print(f'Error: {msg}')


@pytest.mark.asyncio
async def test_abci_info(noderpc):
    resp = await noderpc.get_abci_info()
    assert "result" in resp


@pytest.mark.asyncio
async def test_consensus_state(noderpc):
    resp = await noderpc.get_consensus_state()
    assert "result" in resp


@pytest.mark.asyncio
async def test_get_dump_consensus_state(noderpc):
    resp = await noderpc.get_dump_consensus_state()
    assert "result" in resp


@pytest.mark.asyncio
async def test_get_genesis(noderpc):
    resp = await noderpc.get_genesis()
    assert "result" in resp


@pytest.mark.asyncio
async def test_get_health(noderpc):
    resp = await noderpc.get_health()
    assert "result" in resp


@pytest.mark.asyncio
async def test_net_info(noderpc):
    resp = await noderpc.get_net_info()
    assert "result" in resp


@pytest.mark.asyncio
async def test_get_num_unconfirmed_txs(noderpc):
    resp = await noderpc.get_num_unconfirmed_txs()
    assert "result" in resp


@pytest.mark.asyncio
async def test_get_status(noderpc):
    resp = await noderpc.get_status()
    assert "result" in resp


@pytest.mark.asyncio
async def test_abci_query(noderpc):
    resp = await noderpc.abci_query("/param/fees")
    assert "result" in resp


@pytest.mark.asyncio
async def test_block(noderpc):
    resp = await noderpc.block()
    assert "result" in resp


@pytest.mark.asyncio
async def test_block_by_hash(noderpc):
    resp = await noderpc.block_by_hash(
        "8B43B22699803E8F8E51E7D9294C14EDAD34A264ECFB7F776AF9422714B93C06"
    )
    assert "error" in resp


@pytest.mark.asyncio
async def test_block_results(noderpc):
    resp = await noderpc.block_results()
    assert "result" in resp


@pytest.mark.asyncio
async def test_blockchain(noderpc):
    resp = await noderpc.blockchain("0", "1")
    assert "result" in resp


@pytest.mark.asyncio
async def test_broadcast_tx_async(noderpc):
    resp = await noderpc.broadcast_tx_async(
        "0xdb01f0625dee0a63ce6dc0430a14813e4939f1567b219704ffc2ad4df58bde010879122b383133453439333946313536374232313937303446464332414434444635384244453031303837392d34341a0d5a454252412d3136445f424e422002280130c0843d38904e400112700a26eb5ae9872102139bdd95de72c22ac2a2b0f87853b1cca2e8adf9c58a4a689c75d3263013441a124015e99f7a686529c76ccc2d70b404af82ca88dfee27c363439b91ea0280571b2731c03b902193d6a5793baf64b54bcdf3f85e0d7cf657e1a1077f88143a5a65f518d2e518202b"
    )
    assert "result" in resp


@pytest.mark.asyncio
async def test_broadcast_tx_commit(noderpc):
    resp = await noderpc.broadcast_tx_commit(
        "0xdb01f0625dee0a63ce6dc0430a14813e4939f1567b219704ffc2ad4df58bde010879122b383133453439333946313536374232313937303446464332414434444635384244453031303837392d34341a0d5a454252412d3136445f424e422002280130c0843d38904e400112700a26eb5ae9872102139bdd95de72c22ac2a2b0f87853b1cca2e8adf9c58a4a689c75d3263013441a124015e99f7a686529c76ccc2d70b404af82ca88dfee27c363439b91ea0280571b2731c03b902193d6a5793baf64b54bcdf3f85e0d7cf657e1a1077f88143a5a65f518d2e518202b"
    )
    assert "result" in resp


@pytest.mark.asyncio
async def test_broadcast_tx_sync(noderpc):
    resp = await noderpc.broadcast_tx_sync(
        "0xdb01f0625dee0a63ce6dc0430a14813e4939f1567b219704ffc2ad4df58bde010879122b383133453439333946313536374232313937303446464332414434444635384244453031303837392d34341a0d5a454252412d3136445f424e422002280130c0843d38904e400112700a26eb5ae9872102139bdd95de72c22ac2a2b0f87853b1cca2e8adf9c58a4a689c75d3263013441a124015e99f7a686529c76ccc2d70b404af82ca88dfee27c363439b91ea0280571b2731c03b902193d6a5793baf64b54bcdf3f85e0d7cf657e1a1077f88143a5a65f518d2e518202b"
    )
    assert "result" in resp


@pytest.mark.asyncio
async def test_commit(noderpc):
    resp = await noderpc.commit("1")
    assert "result" in resp


@pytest.mark.asyncio
async def test_consensus_params(noderpc):
    resp = await noderpc.consensus_params("1")
    assert "result" in resp


@pytest.mark.asyncio
async def test_tx(noderpc):
    resp = await noderpc.tx("36F0945A22CD6921FF9F85F64080334B4887DE4021B2EA5EE7B1D182C3FFEE01")
    assert "error" in resp


@pytest.mark.asyncio
async def test_tx_search(noderpc):
    resp = await noderpc.tx_search("tx.height=1000", per_page=1)
    assert "result" in resp


@pytest.mark.asyncio
async def test_unconfirmed_txs(noderpc):
    resp = await noderpc.unconfirmed_txs()
    assert "result" in resp


@pytest.mark.asyncio
async def test_validators(noderpc):
    resp = await noderpc.validators()
    assert "result" in resp


@pytest.mark.asyncio
async def test_invalid_post_request(noderpc):
    noderpc.url = "https://binance.org/invalid"
    try:
        resp = await noderpc.post_request('INVALID')
        assert False, resp
    except BinanceChainException as e:
        assert e.response.status == 403
        assert isinstance(e.__cause__, aiohttp.ContentTypeError)


@pytest.mark.asyncio
async def test_invalid_get_request(noderpc):
    try:
        resp = await noderpc.get_request('INVALID')
        assert False, resp
    except BinanceChainException as e:
        assert e.response.status == 404
        assert isinstance(e.__cause__, aiohttp.ContentTypeError)


@pytest.mark.asyncio
async def test_del_without_close_warning():
    noderpc = NodeRPC(testnet=True)
    await noderpc.get_status()
    with pytest.warns(UserWarning):
        del(noderpc)


@pytest.mark.asyncio
async def test_ws_open_close(noderpc):
    """"Open then immediately close"""
    def on_open():
        print('opened')
        noderpc.close()

    await noderpc.start_async(on_open=on_open, on_error=on_error)
    print('closed')


@pytest.mark.asyncio
async def test_ws_subscribe(noderpc):
    """"Open then immediately close with the decorator API"""

    results = []

    def on_msg(msg):
        results.append(msg)
        noderpc.close()

    def on_open():
        noderpc.subscribe("tm.event = 'Tx'")

    await noderpc.start_async(on_open=on_open, on_error=on_error, on_msg=on_msg)
    assert results
    result_ids = [r['id'] for r in results]
    assert result_ids == ['0']
    for result in results:
        assert result['result'] == {}


@pytest.mark.asyncio
async def test_ws_unsubscribe(noderpc):
    """"Open then immediately close with the decorator API"""

    results = []

    def on_msg(msg):
        print('on_msg', msg)
        results.append(msg)
        if len(results) == 1:
            noderpc.unsubscribe("tm.event = 'Tx'")
        if len(results) == 2:
            noderpc.close()

    def on_open():
        noderpc.subscribe("tm.event = 'Tx'")

    await noderpc.start_async(on_open=on_open, on_error=on_error, on_msg=on_msg)
    assert results
    result_ids = [r['id'] for r in results]
    assert result_ids == ['0', '1']
    for result in results:
        assert result['result'] == {}


@pytest.mark.asyncio
async def test_ws_unsubscribe_all(noderpc):
    """"Open then immediately close with the decorator API"""

    results = []

    def on_msg(msg):
        print('on_msg', msg)
        results.append(msg)
        if len(results) == 1:
            noderpc.unsubscribe_all()
        if len(results) == 2:
            noderpc.close()

    def on_open():
        noderpc.subscribe("tm.event = 'Tx'")

    await noderpc.start_async(on_open=on_open, on_error=on_error, on_msg=on_msg)
    assert results
    result_ids = [r['id'] for r in results]
    assert result_ids == ['0', '1']
    for result in results:
        assert result['result'] == {}
