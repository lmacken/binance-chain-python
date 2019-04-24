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
    pubkey, signature = wallet.sign_transaction(transaction.StdSignMsg)
    transaction.update_signature(pubkey, signature)
    print(transaction.txblob)
    broadcast = await chain.broadcast(transaction.txblob)
    txid = broadcast[0]["hash"]
    tx = await chain.get_transaction(txid)
    print(tx)
    # print(
    #     len(
    #         "de01f0625dee0a66ce6dc0430a14ba36f0fad74d8f41045463e4774f328f4af779e5122b424133364630464144373444384634313034353436334534373734463332384634414637373945352d33331a0d4144412e422d4236335f424e42200428023080c2d72f3880c2d72f4002126e0a26eb5ae98721029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e1240851fc9542342321af63ecbba7d3ece545f2a42bad01ba32cff5535b18e54b6d3106e10b6a4525993d185a1443d9a125186960e028eabfdd8d76cf70a3a7e3100182220202001"
    #     )
    # )
    # br = await chain.broadcast(
    #     "de01f0625dee0a66ce6dc0430a14ba36f0fad74d8f41045463e4774f328f4af779e5122b424133364630464144373444384634313034353436334534373734463332384634414637373945352d33331a0d4144412e422d4236335f424e42200428023080c2d72f3880c2d72f4002126e0a26eb5ae98721029729a52e4e3c2b4a4e52aa74033eedaf8ba1df5ab6d1f518fd69e67bbd309b0e1240851fc9542342321af63ecbba7d3ece545f2a42bad01ba32cff5535b18e54b6d3106e10b6a4525993d185a1443d9a125186960e028eabfdd8d76cf70a3a7e3100182220202001"
    # )
    # print(br)
