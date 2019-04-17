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
        for key in (
            "version",
            "network",
            "moniker",
            "id",
            "capabilities",
        ):
            assert key in peer


# TODO:
# get_transaction(txid)

@pytest.mark.asyncio
async def test_token_list(client):
    tokens = await client.get_token_list()
    pprint(tokens)
    assert False
    for token in tokens:
        for key in ("mintable", 'name', 'original_symbol', 'owner', 'symbol', 'total_supply'):
            assert key in token
