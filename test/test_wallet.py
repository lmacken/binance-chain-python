"""
Binance DEX SDK Test Suite for Wallet builder
"""
from pprint import pprint

import pytest
import asyncio
import json
from decimal import Decimal
from binancechain import BinanceWallet, BinanceChain

MNEMONIC_2 = "tennis utility midnight pattern that foot security tent punch glance still night virus loop trade velvet rent glare ramp cushion defy grass section cage"
MNEMONIC = "apart conduct congress bless remember picnic aerobic nothing dinner guilt catch brain sunny vocal advice castle horror shift reject valley evoke fork syrup code"
PASSWORD = "Alkseui12p,d"
KEYSTORE = None
PRIVATEKEY = None


@pytest.fixture
async def chain():
    chain = BinanceChain(testnet=True)
    yield chain
    await chain.close()


@pytest.mark.asyncio
async def test_create_wallet(chain):
    wallet = BinanceWallet.create_wallet()
    address = wallet.get_address()
    print(wallet)
    assert address, "Failed to get address from wallet"


@pytest.mark.asyncio
async def test_create_wallet_mnemonic(chain):
    wallet = BinanceWallet.create_wallet_mnemonic(password=PASSWORD)
    address = wallet.get_address()
    mnemonic = wallet.get_mnemonic()
    assert address, "Failed to get address from wallet"
    assert mnemonic, "Failed to create wallet with mnemonic"
    assert len(mnemonic.split(" ")) == 24, "Mnemonic length is invalid"


@pytest.mark.asyncio
async def test_create_keystore(chain):
    keystore = BinanceWallet.create_keystore(password=PASSWORD)
    assert keystore, "Failed to create keystore"
    KEYSTORE = keystore
    print(keystore)


@pytest.mark.asyncio
async def test_recover_wallet_keystore(chain):
    wallet = BinanceWallet.recover_from_keystore(keystore=KEYSTORE, password=PASSWORD)
    address = wallet.get_address()
    assert address, "Failed to get address from wallet"


@pytest.mark.asyncio
async def test_recover_wallet_mnemonic(chain):
    wallet = BinanceWallet.recover_from_mnemonic(MNEMONIC, password="")
    address = wallet.get_address()
    PRIVATEKEY = wallet.get_privatekey()
    assert address, "Failed to get address from wallet"


@pytest.mark.asyncio
async def test_recover_wallet_privatekey(chain):
    wallet = BinanceWallet.recover_from_privatekey(privatekey=PRIVATEKEY, password="")
    address = wallet.get_address()
    assert address, "Failed to get address from wallet"
