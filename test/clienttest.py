import pytest

from binancedex.httpclient import BNC


@pytest.fixture
async def client():
    client = BNC(testnet=True)
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_time(client):
    print('Testing init')
    time = await client.get_time()
    print('time =', time)
    assert 'ap_time' in time
    assert 'block_time' in time
