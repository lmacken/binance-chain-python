"""
Binance DEX SDK Test Suite for Transaction builder
"""
from pprint import pprint

import pytest

from binancechain import BinanceTransaction, BinanceWallet, BinanceChain

MNEMONIC = "tennis utility midnight pattern that foot security tent punch glance still night virus loop trade velvet rent glare ramp cushion defy grass section cage"
PAIR = "84SHEDAO-F6F_BNB"


@pytest.fixture
async def chain():
    chain = BinanceChain(testnet=True)
    yield chain
    await chain.close()


@pytest.fixture
async def wallet():
    wallet = BinanceWallet.recover_from_mnemonic(words=MNEMONIC, testnet=True)
    yield wallet


@pytest.mark.asyncio
async def test_new_order(wallet, chain):
    address = wallet.get_address()
    transaction = await BinanceTransaction.new_order(
        address=address, symbol=PAIR, side=1, price=0.001, quantity=1, testnet=True
    )
    print(transaction.StdSignMsg)
    pubkey, signature = wallet.sign_transaction(transaction.StdSignMsg)
    print(pubkey, signature)
    transaction.update_signature(pubkey, signature)
    broadcast = await chain.broadcast(transaction.txblob)
    print(broadcast)
    # transaction.udpate_signature(signature)
