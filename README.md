# binance-chain-python

[![Build Status](https://travis-ci.org/lmacken/binance-chain-python.svg?branch=master)](https://travis-ci.org/lmacken/binance-chain-python)
[![Coverage Status](https://coveralls.io/repos/github/lmacken/binance-chain-python/badge.svg)](https://coveralls.io/github/lmacken/binance-chain-python)

An asyncio-driven Python API for the Binance Chain.

## Installation

    pip install git+https://github.com/lmacken/binance-chain-python.git

## Implementation

- Python3 asyncio + [aiohttp](https://aiohttp.readthedocs.io)
- [bitcoinlib](https://github.com/1200wd/bitcoinlib)
- [secp236k1](https://github.com/ludbb/secp256k1-py)
- Extensive pytest suite
- SPDX license identifiers
- Python3.6+ f-strings
- Type annotations
- Exception-chaining with `raise from`
- Consistent syntax formatting with [Black](https://github.com/ambv/black)

------------------

## WebSocket

  - `aiohttp <https://aiohttp.readthedocs.io>` powered
  - Event-driven, using `pyee <https://github.com/jfhbrook/pyee>`
  - Decorator API for simple usage
  - Automatically sends `keepAlive` messages every 30 minutes

## TODO
 - Rate limiter

### REST API
------------------

### NODE RPC
------------------

### WEBSOCKET
-------------------

#### Decorator API

```python
from binancechain import BinanceChainWebSocket

ADDRESS = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"

dex = BinanceChainWebSocket(ADDRESS, testnet=True)

@dex.on("open")
async def on_open():
    print('Binance Chain WebSocket open')

@dex.on("allTickers", symbols=["$all"])
async def on_ticker(msg):
    print(msg)

try:
    dex.start()
except KeyboardInterrupt:
    pass
finally:
    dex.close()
```


### BINANCE CHAIN WALLET
----------------
#### Create or recover wallet and keystore
```python
from binancechain import BinanceWallet
```
- Create new wallet
```python
wallet = BinanceWallet.create_wallet(password="", testnet=False)

wallet = BinanceWallet.create_wallet_mnemonic(language="english", password="", testnet=False)
```

- Create Keystore
```python
keystore = BinanceWallet.create_keystore(password=None)
```
- Create wallet from HDKey
```python
wallet = BinanceWallet(key="HDKEY object", testnet=False)
```
- Get wallet from keystore
```python
wallet = BinanceWallet.wallet_from_keystore(keystore=keystore, password="", testnet=False)
```
- Get wallet from mnemonic
```python
wallet = BinanceWallet.wallet_from_mnemonic(words="mnemonic words", password="", testnet=False)
```
- Get wallet from private key
```python
wallet = BinanceWallet.wallet_from_privatekey(privatekey="private_key", password="", testnet=False)
```

#### Using the wallet
```python
from binancechain import BinanceWallet

wallet = BinanceWallet.create_wallet(password="", testnet=True)
```
- Get bnb address
```python
address = wallet.get_adress()
```
- Get public and private key
```python
priv = wallet.get_privatekey()

pub = wallet.get_publickey()
```
- Sign message and verify signature
```python
pub, signature = wallet.sign(msg)

is_valid = wallet.verify_signature(msg, signature)
```

### BINANCE CHAIN TRANSACTION
-------------------

#### Using Transaction with wallet and client, handle signing and broadcast internally
```python
from binancechain import BinanceTransaction BinanceWallet

from binancechain.enums import ORDERTYPE, SIDE, TIMEINFORCE, VOTES

#if client is passed in , testnet arg will be ignored

transaction = BinanceTransaction(wallet=wallet, client=None,testnet=False)

  transfer = await transaction.transfer(to_address, symbol, amount)

  broadcast_info = await transaction.create_new_order(
      symbol="binance_pair",
      side=SIDE.Buy,
      ordertype=ORDERTYPE.Limit,
      price=1,
      quantity=1,
      timeInForce=TIMEINFORCE.GTE,
  )

  broadcast_info = await transaction.cancel_order(symbol="pair", refid)

  broadcast_info = await transaction.freeze_token(symbol="token", amount)

  broadcast_info = await transaction.unfreeze_token(symbol="token", amount)

  broadcast_info = await transaction.vote(
      proposal_id="", option=VOTES.Yes
  )
```
#### Create Transaction Message. This message can be signed and broadcast somewhere else

```python
limit_buy_transaction = await BinanceTransaction.new_order_transaction(
      address="owner address",
      symbol="pair",
      side=SIDE.Buy,
      ordertype=ORDERTYPE.Limit,
      price=1,
      quantity=1,
      timeInForce=TIMEINFORCE.GTE,
      testnet=True,
  )

  limit_sell_transaction = await BinanceTransaction.new_order_transaction(
      address="owner address",
      symbol="pair",
      side=SIDE.Buy,
      ordertype=ORDERTYPE.Limit,
      price=1,
      quantity=1,
      timeInForce=TIMEINFORCE.GTE,
      testnet=True,
  )

  cancel_order_transaction = await BinanceTransaction.cancel_order(
      address="owner_address", symbol="pair", refid="", testnet=True
  )

  freeze_token_transaction = await BinanceTransaction.freeze_token(
      address="ownder_address", symbol="token", amount=1, testnet=True
  )

  unfreeze_token_tranasaction = await BinanceTransaction.unfreeze_token_transaction(
      address="ownder_address", symbol="token", amount=1, testnet=True
  )
```
- Example transaction message :

```
b'{"account_number":"668107","chain_id":"Binance-Chain-Nile","data":null,"memo":"","msgs":[{"inputs":[{"address":"tbnb1r5jc35v338tlphnjx65wy7tecm6vm82tftfkt7","coins":[{"amount":10000000,"denom":"BNB"}]}],"outputs":[{"address":"tbnb1nhvpuq0u5pgpry0x2ap2hqv9n5jfkj90eps6qx","coins":[{"amount":10000000,"denom":"BNB"}]}]}],"sequence":"35","source":"1"}'
```

### Running the test suite
----------------------

```bash
git clone https://github.com/lmacken/binance-chain-python.git
pip install -r test-requirements.txt`
python setup.py develop
pytest
```
