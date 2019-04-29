import asyncio
import pytest

from binancechain import HTTPClient


@pytest.mark.asyncio
async def test_ratelimiter():
    """
    Make 10 `time` requests concurrently and ensure they are not rate-limited
    """
    client = HTTPClient(testnet=True, rate_limit=True)
    futures = []
    for _ in range(10):
        futures.append(asyncio.ensure_future(client.get_time()))

    results = await asyncio.gather(*futures)
    print(results)
    assert results
    for result in results:
        print(result)
        if 'message' in result:
            assert result['message'] != 'API rate limit exceeded'
        assert 'block_time' in result

    await client.close()
