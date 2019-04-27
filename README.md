Implementation Details
----------------------

- Python3 asyncio
- asyncio
- aiohttp
- bitcoinlib
- secp236k1

    connection pooling?

REST HTTP Client
Node RPC Client
Wallet
Transaction Builder

WebSocket
  - `aiohttp <https://aiohttp.readthedocs.io>` powered
  - Event-driven, using `pyee <https://github.com/jfhbrook/pyee>`
  - Decorator API for simple usage
  - Automatically sends `keepAlive` messages every 30 minutes


SDK features
------------
    - CLI
    - Rate limiter (TODO)


Best Practices
--------------
- Extensive pytest suite
- SPDX license identifiers
- Python3.6+ f-strings
- Type annotations
- Exception-chaining with `raise from`
- Consistent syntax formatting with `Black <https://github.com/ambv/black>`




### REST API
------------------

### NODE RPC
------------------

### WEBSOCKET
-------------------

### BINANCE CHAIN WALLET
----------------
#### Create or recover wallet and keystore
```
from binancechain import BinanceWallet

wallet = BinanceWallet.create_wallet(password="", testnet=False)

wallet = BinanceWallet.create_wallet_mnemonic(
    language="english", password="", testnet=False
)

keystore = BinanceWallet.create_keystore(password="")

wallet = BinanceWallet(key="HDKEY object", testnet=False)

wallet = BinanceWallet.wallet_from_keystore(
    keystore=keystore, password="", testnet=False
)

wallet = BinanceWallet.wallet_from_mnemonic(
    words="mnemonic words", password="", testnet=False
)

wallet = BinanceWallet.wallet_from_privatekey(
    privatekey="private_key", password="", testnet=False
)
```

#### Using wallet
```
from binancechain import BinanceWallet

wallet = BinanceWallet.create_wallet(password="", testnet=True)

address = wallet.get_adress()

priv = wallet.get_privatekey()

pub = wallet.get_publickey()

pub,signature = wallet.sign(b'"msg")

is_valid:bool = wallet.verify_signature(b'"msg",signature)
```

### BINANCE CHAIN TRANSACTION
-------------------

#### Using Transaction with wallet and client, handle signing and broadcast internally
```
from binancechain import BinanceTransaction BinanceWallet

from binancechain.enums import ORDERTYPE, SIDE, TIMEINFORCE, VOTES

#if client is passed in , testnet arg will be ignored

transaction = BinanceTransaction(wallet=wallet, client=client)

  transfer = await transaction.transfer(
      to_address=wallet_two.get_address(), symbol="BNB", amount=0.1
  )

  broadcast_info = await transaction.create_new_order(
      symbol="binance_pair",
      side=SIDE.Buy,
      ordertype=ORDERTYPE.Limit,
      price=1,
      quantity=1,
      timeInForce=TIMEINFORCE.GTE,
  )

  broadcast_info = await transaction.cancel_order(symbol="pair", refid="")

  broadcast_info = await transaction.freeze_token(symbol="token", amount=1)

  broadcast_info = await transaction.unfreeze_token(symbol="token", amount=1)

  broadcast_info = await transaction.vote(
      proposal_id="", option=VOTES.Yes
  )
```
#### Create Transaction Message. This message can be signed and broadcast somewhere else

```
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

```b'{"account_number":"668107","chain_id":"Binance-Chain-Nile","data":null,"memo":"","msgs":[{"inputs":[{"address":"tbnb1r5jc35v338tlphnjx65wy7tecm6vm82tftfkt7","coins":[{"amount":10000000,"denom":"BNB"}]}],"outputs":[{"address":"tbnb1nhvpuq0u5pgpry0x2ap2hqv9n5jfkj90eps6qx","coins":[{"amount":10000000,"denom":"BNB"}]}]}],"sequence":"35","source":"1"}'```

### Running the test suite
----------------------

```git clone https://github.com/lmacken/binance-chain-python
pip install -r test-requirements.txt
python setup.py develop
pytest -v --cov=binancechain
```
