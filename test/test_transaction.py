# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
Binance DEX SDK Test Suite for Transaction builder
"""
from pprint import pprint

import pytest
import asyncio
import json
from decimal import Decimal

import binascii

from binancechain import Transaction, Wallet, HTTPClient, BinanceChainException
from binancechain.enums import Side, Votes, Ordertype, Timeinforce

MNEMONIC_2 = "tennis utility midnight pattern that foot security tent punch glance still night virus loop trade velvet rent glare ramp cushion defy grass section cage"
MNEMONIC = "apart conduct congress bless remember picnic aerobic nothing dinner guilt catch brain sunny vocal advice castle horror shift reject valley evoke fork syrup code"
PAIR = "IBB-8DE_BNB"
PROPOSAL_ID = 370


@pytest.fixture
async def client():
    client = HTTPClient(testnet=True)
    yield client
    await client.close()


@pytest.fixture
async def wallet():
    wallet = Wallet.wallet_from_mnemonic(words=MNEMONIC, testnet=True)
    yield wallet


@pytest.fixture
async def wallet_two():
    wallet_two = Wallet.wallet_from_mnemonic(words=MNEMONIC_2, testnet=True)
    yield wallet_two


@pytest.mark.asyncio
async def test_new_order(wallet, client):
    address = wallet.get_address()
    transaction = await Transaction.new_order_transaction(
        address=address,
        symbol=PAIR,
        side=Side.BUY,
        timeInForce=Timeinforce.GTE,
        price=0.01,
        quantity=1,
        ordertype=Ordertype.LIMIT,
        client=client,
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await client.broadcast(hex_data)
    txid = broadcast[0]["hash"]
    assert txid
    await asyncio.sleep(2)
    tx = await client.get_transaction(txid)
    assert tx["data"], "transaction not found"
    print(tx)


@pytest.mark.asyncio
async def test_cancel_order(wallet, client):
    address = wallet.get_address()
    open_orders = await client.get_open_orders(address)
    order = open_orders["order"][0]
    refid = order["orderId"]
    symbol = order["symbol"]
    transaction = await Transaction.cancel_order_transaction(
        address=address, symbol=symbol, refid=refid, client=client
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await client.broadcast(hex_data)
    txid = broadcast[0]["hash"]
    await asyncio.sleep(2)
    tx = await client.get_transaction(txid)
    assert tx["data"], "transaction not found"


@pytest.mark.asyncio
async def test_transfer_order(wallet, wallet_two, client):
    address_1 = wallet.get_address()
    address_2 = wallet_two.get_address()
    account_1 = await client.get_account(address_1)
    account_2 = await client.get_account(address_2)
    balances_1 = account_1["balances"]
    balances_2 = account_2["balances"]
    TOKEN = "BNB"
    for balance in balances_1:
        if balance["symbol"] == TOKEN:
            balance_1 = Decimal(balance["free"])
            break
    for balance in balances_2:
        if balance["symbol"] == TOKEN:
            balance_2 = Decimal(balance["free"])
            break
    assert balance_1 and balance_1 > 0.1, "No Token balance to test"
    transaction = await Transaction.transfer_transaction(
        from_address=address_1,
        to_address=address_2,
        symbol=TOKEN,
        amount=0.1,
        client=client,
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await client.broadcast(hex_data)
    assert broadcast, "Fail to broadcast"
    assert "hash" in broadcast[0], "No txid"
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await client.get_transaction(txid)
    assert tx, "No transaction on client"
    assert "data" in tx, "tx is not on chain"
    print(tx)
    # TODO check balance again


@pytest.mark.asyncio
async def test_multi_transfer_order(wallet, wallet_two, client):
    address_1 = wallet.get_address()
    address_2 = wallet_two.get_address()
    account_1 = await client.get_account(address_1)
    account_2 = await client.get_account(address_2)
    TOKEN_1 = "BNB"
    TOKEN_2 = "BTC-531"
    AMOUNT = 0.001
    transfers = [
        {"symbol": TOKEN_1, "amount": AMOUNT},
        {"symbol": TOKEN_2, "amount": AMOUNT},
    ]
    transaction = await Transaction.multi_transfer_transaction(
        from_address=address_2, to_address=address_1, transfers=transfers, client=client
    )
    pubkey, signature = wallet_two.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await client.broadcast(hex_data)
    assert broadcast, "Fail to broadcast"
    assert "hash" in broadcast[0], "No txid"
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await client.get_transaction(txid)
    assert tx, "No transaction on client"
    assert "data" in tx, "tx is not on chain"
    print(tx)


@pytest.mark.asyncio
async def test_freeze_token(wallet, client):
    address = wallet.get_address()
    transaction = await Transaction.freeze_token_transaction(
        address=address, symbol="BNB", amount=0.0001, client=client
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await client.broadcast(hex_data)
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await client.get_transaction(txid)
    print(tx)


@pytest.mark.asyncio
async def test_unfreeze_token(wallet, client):
    address = wallet.get_address()
    transaction = await Transaction.unfreeze_token_transaction(
        address=address, symbol="BNB", amount=0.0001, client=client
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await client.broadcast(hex_data)
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await client.get_transaction(txid)


@pytest.mark.asyncio
async def test_transaction_object_new_order(wallet, client):
    address = wallet.get_address()
    transaction = Transaction(wallet=wallet, client=client)
    new_order = await transaction.create_new_order(
        symbol=PAIR,
        side=Side.BUY,
        timeInForce=Timeinforce.GTE,
        price=0.01,
        quantity=1,
        ordertype=Ordertype.LIMIT,
    )
    assert new_order, "No result of new_order found"
    assert new_order[0]["hash"], "No txid found"
    await asyncio.sleep(1)
    tx = await client.get_transaction(new_order[0]["hash"])
    assert tx, "Transaction not on chain"


@pytest.mark.asyncio
async def test_transaction_object_cancel(wallet, client):
    address = wallet.get_address()
    open_orders = await client.get_open_orders(address)
    order = open_orders["order"][0]
    refid = order["orderId"]
    symbol = order["symbol"]
    transaction = Transaction(wallet=wallet, client=client)
    cancel_order = await transaction.cancel_order(symbol=symbol, refid=refid)
    print(cancel_order)
    assert cancel_order, "No result of cancel found"
    assert cancel_order[0]["hash"], "No txid found"
    await asyncio.sleep(1)
    tx = await client.get_transaction(cancel_order[0]["hash"])
    assert tx, "Transaction not on chain"


@pytest.mark.asyncio
async def test_transaction_object_transfer(wallet, wallet_two, client):
    transaction = Transaction(wallet=wallet, client=client)
    transfer = await transaction.transfer(
        to_address=wallet_two.get_address(), symbol="BNB", amount=0.1
    )
    assert transfer, "No result of transfer found"
    assert transfer[0]["hash"], "No txid found"
    await asyncio.sleep(1)
    tx = await client.get_transaction(transfer[0]["hash"])
    assert tx, "Transaction not on chain"


@pytest.mark.asyncio
async def test_multi_transaction_object_transfer(wallet, wallet_two, client):
    transaction = Transaction(wallet=wallet_two, client=client)
    TOKEN_1 = "BNB"
    TOKEN_2 = "BTC-531"
    AMOUNT = 0.002
    transfers = [
        {"symbol": TOKEN_1, "amount": AMOUNT},
        {"symbol": TOKEN_2, "amount": AMOUNT},
    ]
    transfer = await transaction.multi_transfer(
        to_address=wallet.get_address(), transfers=transfers
    )
    assert transfer, "No result of transfer found"
    assert transfer[0]["hash"], "No txid found"
    await asyncio.sleep(1)
    tx = await client.get_transaction(transfer[0]["hash"])
    assert tx, "Transaction not on chain"


@pytest.mark.asyncio
async def test_transaction_object_freeze(wallet, client):
    transaction = Transaction(wallet=wallet, client=client)
    freeze = await transaction.freeze_token(symbol="BNB", amount=0.1)
    print(freeze)
    assert freeze, "No result of freeze found"
    assert freeze[0]["hash"], "No txid found"
    await asyncio.sleep(1)
    tx = await client.get_transaction(freeze[0]["hash"])
    assert tx, "Transaction not on chain"


@pytest.mark.asyncio
async def test_transaction_object_unfreeze(wallet, client):
    transaction = Transaction(wallet=wallet, client=client)
    unfreeze = await transaction.unfreeze_token(symbol="BNB", amount=0.1)
    print(unfreeze)
    assert unfreeze, "No result of unfreeze found"
    assert unfreeze[0]["hash"], "No txid found"
    await asyncio.sleep(1)
    tx = await client.get_transaction(unfreeze[0]["hash"])
    assert tx, "Transaction not on chain"


@pytest.mark.asyncio
async def test_transaction_object_burn(wallet_two, client):
    transaction = Transaction(wallet=wallet_two, client=client)
    burn = await transaction.burn_token(symbol="BTC-531", amount=1)
    print(burn)
    assert burn, "No result of unfreeze found"
    assert burn[0]["hash"], "No txid found"
    await asyncio.sleep(1)
    tx = await client.get_transaction(burn[0]["hash"])
    assert tx, "Transaction not on chain"
    print(tx)


@pytest.mark.asyncio
async def test_issue_token(wallet_two, client):
    address = wallet_two.get_address()
    transaction = await Transaction.issue_token_transaction(
        owner=address,
        name="Bitcoin",
        symbol="BTC",
        supply=1000000000000000,
        mintable=True,
        client=client,
    )
    pubkey, signature = wallet_two.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    print(binascii.hexlify(transaction.stdTx))
    broadcast = await client.broadcast(hex_data)
    assert broadcast, "No result of issue found"
    assert broadcast[0]["hash"], "No txid found"
    # TODO need 400 BNB on testnet to issue
    # txid = broadcast[0]["hash"]
    # await asyncio.sleep(1)
    # tx = await client.get_transaction(txid)
    # print(tx)


@pytest.mark.asyncio
async def test_mint_token(wallet_two, client):
    address = wallet_two.get_address()
    transaction = await Transaction.mint_token_transaction(
        owner=address, symbol="BTC-531", amount=10000, client=client
    )
    pubkey, signature = wallet_two.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    print(binascii.hexlify(transaction.stdTx))
    broadcast = await client.broadcast(hex_data)
    assert broadcast, "No result of mint found"
    assert broadcast[0]["hash"], "No txid found"
    # TODO need 200 BNB on testnet to mint
    # txid = broadcast[0]["hash"]
    # await asyncio.sleep(1)
    # tx = await client.get_transaction(txid)
    # print(tx)


@pytest.mark.asyncio
async def test_burn_token(wallet_two, client):
    address = wallet_two.get_address()
    print(address)
    transaction = await Transaction.burn_token_transaction(
        owner=address, symbol="BTC-531", amount=1, client=client
    )
    pubkey, signature = wallet_two.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    print(binascii.hexlify(transaction.stdTx))
    broadcast = await client.broadcast(hex_data)
    txid = broadcast[0]["hash"]
    await asyncio.sleep(1)
    tx = await client.get_transaction(txid)
    print(tx)


@pytest.mark.asyncio
async def test_vote_token(wallet, client):
    address = wallet.get_address()
    transaction = await Transaction.vote_transaction(
        voter=address, proposal_id=PROPOSAL_ID, option=Votes.YES, client=client
    )
    pubkey, signature = wallet.sign(transaction.get_sign_message())
    hex_data = transaction.update_signature(pubkey, signature)
    broadcast = await client.broadcast(hex_data)
    assert broadcast, "No result of vote found"
    assert broadcast[0]["hash"], "No txid found"
    # TODO need to be validator to vote
    # txid = broadcast[0]["hash"]
    # await asyncio.sleep(1)
    # tx = await client.get_transaction(txid)
    # print(tx)
