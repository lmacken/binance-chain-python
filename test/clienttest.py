import pytest

from binancedex.httpclient import BNC


@pytest.mark.asyncio
async def test_init():
    print('Testing init')
    dex = BNC()
    print(dex)
