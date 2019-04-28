# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
Binance DEX SDK Test Suite for Wallet builder
"""
from pprint import pprint

import pytest
import asyncio
import json
from decimal import Decimal
from binancechain import Wallet, HTTPClient

MNEMONIC_2 = "tennis utility midnight pattern that foot security tent punch glance still night virus loop trade velvet rent glare ramp cushion defy grass section cage"
MNEMONIC = "apart conduct congress bless remember picnic aerobic nothing dinner guilt catch brain sunny vocal advice castle horror shift reject valley evoke fork syrup code"
PASSWORD = "Alkseui12p,d"
KEYSTORE = {
    "address": "309ac34e39715899735bfaed1677ff82b5bf35e0",
    "crypto": {
        "cipher": "aes-128-ctr",
        "cipherparams": {"iv": "bab8a3ace08205c897a8a69ddb9bf056"},
        "ciphertext": "6b273686d7858feac0708d64acdd9bdb353191d4f735e8c04a11ee3a31f08f0f",
        "kdf": "pbkdf2",
        "kdfparams": {
            "c": 1000000,
            "dklen": 32,
            "prf": "hmac-sha256",
            "salt": "ed2e6c05ec3e5e49c3519a07d0572cf0",
        },
        "mac": "f11eb5068e3e697c1eeeccd4c5f167c6fc0956f40b3f0cb1588ccd4f0b9d7a13",
    },
    "id": "a0c93b32-6a63-4346-aafa-afdc2b5637dd",
    "version": 3,
}

PRIVATEKEY = "14ffce9d61a219f3b24c0a093a24837368e2317b1e96d77f80505df49c2224c3"
ADDRESS = "bnb1r5jc35v338tlphnjx65wy7tecm6vm82t87qjt0"
TRANSACTION_MSG = b'{"account_number":"668107","chain_id":"Binance-Chain-Nile","data":null,"memo":"","msgs":[{"inputs":[{"address":"tbnb1r5jc35v338tlphnjx65wy7tecm6vm82tftfkt7","coins":[{"amount":10000000,"denom":"BNB"}]}],"outputs":[{"address":"tbnb1nhvpuq0u5pgpry0x2ap2hqv9n5jfkj90eps6qx","coins":[{"amount":10000000,"denom":"BNB"}]}]}],"sequence":"35","source":"1"}'


@pytest.fixture
async def chain():
    chain = HTTPClient(testnet=True)
    yield chain
    await chain.close()


@pytest.fixture
async def wallet():
    wallet = Wallet.wallet_from_privatekey(privatekey=PRIVATEKEY, password="")
    yield wallet


@pytest.mark.asyncio
async def test_create_wallet(chain):
    wallet = Wallet.create_wallet()
    address = wallet.get_address()
    print(wallet)
    assert address, "Failed to get address from wallet"


@pytest.mark.asyncio
async def test_create_wallet_mnemonic(chain):
    wallet = Wallet.create_wallet_mnemonic(password=PASSWORD)
    address = wallet.get_address()
    assert address, "Failed to get address from wallet"


@pytest.mark.asyncio
async def test_create_keystore(chain):
    keystore = Wallet.create_keystore(password=PASSWORD)
    assert keystore, "Failed to create keystore"


@pytest.mark.asyncio
async def test_wallet_from_keystore(chain):
    keystore = Wallet.create_keystore(password=PASSWORD)
    assert keystore, "Failed to create keystore"
    wallet = Wallet.wallet_from_keystore(keystore=keystore, password=PASSWORD)
    address = wallet.get_address()
    assert address, "Failed to get address from recovered wallet"


@pytest.mark.asyncio
async def test_not_recover_wallet_keystore_with_wrong_password(chain):
    keystore = Wallet.create_keystore(password=PASSWORD)
    assert keystore, "Failed to create keystore"
    try:
        wallet = Wallet.wallet_from_keystore(keystore=keystore, password="")
        assert False
    except ValueError as e:
        print(e)
        assert True


@pytest.mark.asyncio
async def test_wallet_from_mnemonic(chain):
    wallet = Wallet.wallet_from_mnemonic(MNEMONIC, password="")
    address = wallet.get_address()
    privatekey = wallet.get_privatekey()
    assert address, "Failed to get address from wallet"
    assert privatekey, "Failed to get private key from wallet"
    assert privatekey == PRIVATEKEY, "Failed to get private key from wallet"
    assert address == ADDRESS, "Not getting the same address from recover"


@pytest.mark.asyncio
async def test_wallet_from_privatekey(chain):
    wallet = Wallet.wallet_from_privatekey(privatekey=PRIVATEKEY, password="")
    address = wallet.get_address()
    assert address, "Failed to get address from wallet"
    assert address == ADDRESS, "Not getting the same address from recover"


@pytest.mark.asyncio
async def test_signing_msg(wallet, chain):
    pub, sig = wallet.sign(TRANSACTION_MSG)
    assert pub, "No public key return"
    assert sig, "No signature return"


@pytest.mark.asyncio
async def test_verify_signature(chain, wallet):
    pub, sig = wallet.sign(TRANSACTION_MSG)
    valid = wallet.verify_signature(TRANSACTION_MSG, signature=sig)
    assert pub, "No public key return"
    assert sig, "No signature return"
    assert valid, "Invalid signature"
