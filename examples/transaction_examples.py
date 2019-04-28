"""
Example to use BinanceTransction for transaction creation
"""

from binancechain import Transaction
from binancechain.enums import Side, Ordertype, Timeinforce


async def transaction_example():
    transaction = Transaction(wallet=wallet, client=client)

    transfer = await transaction.transfer(
        to_address=wallet_two.get_address(), symbol="BNB", amount=0.1
    )

    broadcast_info = await transaction.create_new_order(
        symbol="binance_pair",
        side=Side.BUY,
        ordertype=Ordertype.LIMIT,
        price=1,
        quantity=1,
        timeInForce=Timeinforce.GTE,
    )

    broadcast_info = await transaction.cancel_order(symbol="pair", refid="")

    broadcast_info = await transaction.freeze_token(symbol="token", amount=1)

    broadcast_info = await transaction.unfreeze_token(symbol="token", amount=1)

    broadcast_info = await transaction.vote(
        proposal_id="", option=Votes.YES
    )  # only validator can vote

    """
    Create Unsigned Transaction, return transaction with message to sign and broadcast somewhere else
    """
    """
    Using default client if no client is passed in
    """
    limit_buy_transaction = await Transaction.new_order_transaction(
        address="owner address",
        symbol="pair",
        side=Side.BUY,
        ordertype=Ordertype.LIMIT,
        price=1,
        quantity=1,
        timeInForce=Timeinforce.GTE,
        testnet=True,
    )

    limit_sell_transaction = await Transaction.new_order_transaction(
        address="owner address",
        symbol="pair",
        side=Side.BUY,
        ordertype=Ordertype.LIMIT,
        price=1,
        quantity=1,
        timeInForce=Timeinforce.GTE,
        testnet=True,
    )

    cancel_order_transaction = await Transaction.cancel_order(
        address="owner_address", symbol="pair", refid="", testnet=True
    )

    freeze_token_transaction = await Transaction.freeze_token(
        address="ownder_address", symbol="token", amount=1, testnet=True
    )

    unfreeze_token_tranasaction = await Transaction.unfreeze_token_transaction(
        address="ownder_address", symbol="token", amount=1, testnet=True
    )

    """
    Get information from transaction object
    """
    sign_message_bytes_format = Limit_Buy_Transaction.get_sign_message()
