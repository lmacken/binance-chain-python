"""
Example to use BinanceTransction for transaction creation
"""

from binancechain import BinanceTransaction
from binancechain.enums import SIDE, ORDERTYPE,TIMEINFORCE

"""Create Transaction with key"""
transaction = BinanceTransaction(
    wallet="BinanceWallet", client=None, testnet="bool, will be ignore if client is passed in"
)

broadcast_info = await transaction.transfer(to_address="address", symbol="token",amount=1)


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

broadcast_info = await transaction.vote(proposal_id="", option=VOTES.Yes)  # only validator can vote
"""
Create Unsigned Transaction, return transaction with message to sign and broadcast somewhere else
"""

limit_buy_transaction =await  BinanceTransaction.new_order_transaction(
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


cancel_order_transaction =await  BinanceTransaction.cancel_order(address="owner_address",symbol="pair",refid="")

freeze_token_transaction = await BinanceTransaction.freeze_token(address="ownder_address",symbol="token",amount=1)

unfreeze_token_tranasaction = await BinanceTransaction.unfreeze_token_transaction(address="ownder_address",symbol="token",amount=1)

"""
Get information from transaction object
"""
sign_message_bytes_format=Limit_Buy_Transaction.get_sign_message()
