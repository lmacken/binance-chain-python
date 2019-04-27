# binance-chain-python

[![Build Status](https://travis-ci.org/lmacken/binance-chain-python.svg?branch=master&color=green)](https://travis-ci.org/lmacken/binance-chain-python)
[![Coverage Status](https://coveralls.io/repos/github/lmacken/binance-chain-python/badge.svg)](https://coveralls.io/github/lmacken/binance-chain-python)
![GitHub](https://img.shields.io/github/license/lmacken/binance-chain-python.svg)

An asyncio-driven Python API for the Binance Chain.

## Installation

    pip install git+https://github.com/lmacken/binance-chain-python.git

## Implementation Details

- [Extensive test suite](https://github.com/lmacken/binance-chain-python/tree/master/test)
- [aiohttp](https://aiohttp.readthedocs.io) for all HTTP requests, which automatically performs connection-pooling
- [SPDX license identifiers](https://spdx.org/)
- Python [type hints](https://docs.python.org/3/library/typing.html) for ease of development
- Python3.6+ f-strings for faster string interpolation
- Exception-chaining with [`raise from`](https://docs.python.org/3/library/exceptions.html#built-in-exceptions)
- Clean and consistent syntax formatting with [Black](https://github.com/ambv/black)

### Utilizes popular crypto libraries
- [bitcoinlib](https://github.com/1200wd/bitcoinlib)
- [bech32](https://github.com/sipa/bech32)
- [secp256k1](https://github.com/ludbb/secp256k1-py)
- [eth_keyfile](https://github.com/ethereum/eth-keyfile)

### WebSocket

- Decorator and callback API for simple WebSocket usage
- Automatically sends `keepAlive` messages every 30 minutes
- Event-driven, using [pyee](https://github.com/jfhbrook/pyee)

------------------

## REST API

### Get information from chain
```python
client = HTTPClient(testnet=True)

server_time = await client.get_time()

node_info = await client.get_node_info()

validators = await client.get_validators()

peers = await client.get_peers()

account_info = await client.get_account_info(address)

sequence_info = await client.get_account_sequence(address)

transaction = await client.get_transaction(hash)

token_list = await client.get_token_list()

markets = await client.get_markets(limit=500, offset=0)

fees = await client.get_fees()

depth = await client.get_depth(symbol, limit=100)

klines = await client.get_klines(symbol, interval, limit=300, start=None, end=None)

closed_orders = await client.get_closed_orders(
    address,
    end=None,
    limit=None,
    offset=None,
    side=None,
    start=None,
    status=None,
    symbol=None,
    total=None,
)

open_orders = await client.get_open_orders(
    self, address, limit=None, offset=None, symbol=None, total=None
)

order = await client.get_order(id)

ticker = await client.get_ticker(symbol)

trades = await client.get_trades(
    address=None,
    buyerOrderId=None,
    height=None,
    limit=None,
    offset=None,
    quoteAsset=None,
    sellerOrderId=None,
    side=None,
    start=None,
    end=None,
    total=None,
    symbol=None,
)

block_fee = await client.block_exchange_fee(
    address=None, end=None, limit=None, offset=None, start=None, total=None
)

transactions = await client.get_transactions(
    address,
    height=None,
    end=None,
    limit=None,
    offset=None,
    side=None,
    start=None,
    tx_asset=None,
    tx_type=None,
)
```
### Broadcast data
```python
broadcast_info = await client.broadcast(data)

```

------------------

## NODE RPC

-------------------

## WEBSOCKET

### Decorator API

```python
from binancechain import nWebSocket

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


----------------

## BINANCE CHAIN WALLET

### Create or recover wallet and keystore
```python
from binancechain import Wallet

wallet = Wallet.create_wallet(password="", testnet=False)

wallet = Wallet.create_wallet_mnemonic(language="english", password="", testnet=False)

keystore = Wallet.create_keystore(password=None)

wallet = Wallet(key="HDKEY object", testnet=False)

wallet = Wallet.wallet_from_keystore(keystore=keystore, password="", testnet=False)

wallet = Wallet.wallet_from_mnemonic(words="mnemonic words", password="", testnet=False)

wallet = Wallet.wallet_from_privatekey(privatekey="private_key", password="", testnet=False)
```

### Using the wallet
```python
from binancechain import Wallet

wallet = Wallet.create_wallet(password="", testnet=True)

address = wallet.get_adress()

priv = wallet.get_privatekey()

pub = wallet.get_publickey()

pub, signature = wallet.sign(msg)

is_valid = wallet.verify_signature(msg, signature)
```

-------------------

## BINANCE CHAIN TRANSACTION

### Using Transaction with wallet and client, handle signing and broadcast internally
```python
from binancechain import Transaction, Wallet

from binancechain.enums import ORDERTYPE, SIDE, TIMEINFORCE, VOTES

#if client is passed in , testnet arg will be ignored

transaction = Transaction(wallet=wallet, client=None,testnet=False)

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
### Create Transaction Message. This message can be signed and broadcast somewhere else

```python
limit_buy_transaction = await Transaction.new_order_transaction(
      address="owner address",
      symbol="pair",
      side=SIDE.Buy,
      ordertype=ORDERTYPE.Limit,
      price=1,
      quantity=1,
      timeInForce=TIMEINFORCE.GTE,
      account_number= None,
      sequence= None,
      client= None,
      testnet = False, # will be ignored if client is passed in
  )

limit_sell_transaction = await Transaction.new_order_transaction(
    address="owner address",
    symbol="pair",
    side=SIDE.Buy,
    ordertype=ORDERTYPE.Limit,
    price=1,
    quantity=1,
    timeInForce=TIMEINFORCE.GTE,
    account_number= None,
    sequence= None,
    client= None,
    testnet = False, # will be ignored if client is passed in
)

cancel_order_transaction = await Transaction.cancel_order(
    address="owner_address",
    symbol="pair",
    refid="",
    account_number= None,
    sequence= None,
    client= None,
    testnet = False, # will be ignored if client is passed in
)

freeze_token_transaction = await Transaction.freeze_token(
    address="ownder_address",
    symbol="token",
    amount=1,
    account_number= None,
    sequence= None,
    client= None,
    testnet = False, # will be ignored if client is passed in
)

unfreeze_token_tranasaction = await Transaction.unfreeze_token_transaction(
    address="ownder_address",
    symbol="token",
    amount=1,
    account_number= None,
    sequence= None,
    client= None,
    testnet = False, # will be ignored if client is passed in
)
```
- Example transaction message :

```
b'{"account_number":"668107","chain_id":"Binance-Chain-Nile","data":null,"memo":"","msgs":[{"inputs":[{"address":"tbnb1r5jc35v338tlphnjx65wy7tecm6vm82tftfkt7","coins":[{"amount":10000000,"denom":"BNB"}]}],"outputs":[{"address":"tbnb1nhvpuq0u5pgpry0x2ap2hqv9n5jfkj90eps6qx","coins":[{"amount":10000000,"denom":"BNB"}]}]}],"sequence":"35","source":"1"}'
```

----------------------

## Running the test suite

```bash
git clone https://github.com/lmacken/binance-chain-python.git
pip install -r test-requirements.txt`
python setup.py develop
pytest
```

----------------------

## Contributors

[@lmacken](https://github.com/lmacken)
[@propulsor](https://github.com/propulsor)
