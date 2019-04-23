"""
Binance DEX SDK Test Suite for Transaction builder
"""
from pprint import pprint

import pytest

from binancechain import BinanceTransaction


@pytest.mark.asyncio
async def test_new_order():
    transaction = await BinanceTransaction.new_order()
