"""
Binance DEX SDK Test Suite for Transaction builder
"""
from pprint import pprint

import pytest
import asyncio
import json
from decimal import Decimal
from binancechain import BinanceTransaction, BinanceWallet, BinanceChain
from binancechain.enums import *

MNEMONIC_2 = "tennis utility midnight pattern that foot security tent punch glance still night virus loop trade velvet rent glare ramp cushion defy grass section cage"
MNEMONIC = "apart conduct congress bless remember picnic aerobic nothing dinner guilt catch brain sunny vocal advice castle horror shift reject valley evoke fork syrup code"
PAIR = "IBB-8DE_BNB"
PROPOSAL_ID = 370


@pytest.fixture
async def chain():
    chain = BinanceChain(testnet=True)
    yield chain
    await chain.close()


@pytest.fixture
async def wallet():
    wallet = BinanceWallet.recover_from_mnemonic(words=MNEMONIC, testnet=True)
    yield wallet


@pytest.fixture
async def wallet_two():
    wallet_two = BinanceWallet.recover_from_mnemonic(words=MNEMONIC_2, testnet=True)
    yield wallet_two


@pytest.mark.asyncio
async def test_new_order(wallet, chain):
    address = wallet.get_address()
    transaction = await BinanceTransaction.new_order_transaction(
        address=address, symbol=PAIR, side=1, price=0.01, quantity=1, testnet=True
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await chain.broadcast(hex_data)
    txid = broadcast[0]["hash"]
    assert txid
    await asyncio.sleep(2)
    tx = await chain.get_transaction(txid)
    print(tx)
    assert tx


@pytest.mark.asyncio
async def test_cancel_order(wallet, chain):
    address = wallet.get_address()
    open_orders = await chain.get_open_orders(address)
    print(len(open_orders))
    order = open_orders["order"][0]
    refid = order["orderId"]
    symbol = order["symbol"]
    transaction = await BinanceTransaction.cancel_order_transaction(
        address=address, symbol=symbol, refid=refid, testnet=True
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await chain.broadcast(hex_data)
    print(broadcast)
    txid = broadcast[0]["hash"]
    await asyncio.sleep(2)
    tx = await chain.get_transaction(txid)
    print(tx)
    assert tx


@pytest.mark.asyncio
async def test_transfer_order(wallet, wallet_two, chain):
    address_1 = wallet.get_address()
    address_2 = wallet_two.get_address()
    account_1 = await chain.get_account(address_1)
    account_2 = await chain.get_account(address_2)
    balances_1 = account_1["balances"]
    balances_2 = account_2["balances"]
    print(balances_1)
    print(balances_2)
    TOKEN = "BNB"
    for balance in balances_1:
        if balance["symbol"] == TOKEN:
            balance_1 = Decimal(balance["free"])
            break
    for balance in balances_2:
        if balance["symbol"] == TOKEN:
            balance_2 = Decimal(balance["free"])
            break
    assert balance_1, "No Token balance to test"
    transaction = await BinanceTransaction.transfer_transaction(
        from_address=address_1,
        to_address=address_2,
        token=TOKEN,
        amount=0.1,
        testnet=True,
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await chain.broadcast(hex_data)
    assert broadcast, "Fail to broadcast"
    assert "hash" in broadcast[0], "No txid"
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await chain.get_transaction(txid)
    assert tx, "No transaction on chain"
    assert "data" in tx, "tx is not on chain"
    # TODO check balance again


@pytest.mark.asyncio
async def test_freeze_token(wallet, chain):
    address = wallet.get_address()
    transaction = await BinanceTransaction.freeze_token_transaction(
        address=address, symbol="BNB", amount=0.0001, testnet=True
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await chain.broadcast(hex_data)
    print(broadcast)
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await chain.get_transaction(txid)
    print(tx)


@pytest.mark.asyncio
async def test_unfreeze_token(wallet, chain):
    address = wallet.get_address()
    transaction = await BinanceTransaction.unfreeze_token_transaction(
        address=address, symbol="BNB", amount=0.0001, testnet=True
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await chain.broadcast(hex_data)
    print(broadcast)
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await chain.get_transaction(txid)
    print(tx)


@pytest.mark.asyncio
async def test_vote_token(wallet, chain):
    print("VOTE", VOTES.Yes.value)
    address = wallet.get_address()
    transaction = await BinanceTransaction.vote_transaction(
        voter=address, proposal_id=PROPOSAL_ID, option=VOTES.Yes, testnet=True
    )
    print("transaction : ", transaction)
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await chain.broadcast(hex_data)
    print(broadcast)
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await chain.get_transaction(txid)
    print(tx)
