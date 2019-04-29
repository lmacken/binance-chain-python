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

    new_order_txid = await transaction.create_new_order(
        symbol="binance_pair",
        side=Side.BUY,
        ordertype=Ordertype.LIMIT,
        price=1,
        quantity=1,
        timeInForce=Timeinforce.GTE,
    )

    cancel_order_txid = await transaction.cancel_order(symbol="pair", refid="")

    freeze_token_txid = await transaction.freeze_token(symbol="token", amount=1)

    unfreeze_token_txid = await transaction.unfreeze_token(symbol="token", amount=1)

    vote_txid = await transaction.vote(
        proposal_id="", option=Votes.YES
    )  # only validator can vote

    issue_token_txid = await transaction.issue_token(symbol, name, supply, mintable)

    mint_token_txid = await transaction.mint_token(symbol, amount)

    burn_token_txid = await transaction.burn_token(symbol, amount)
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
        client=None,
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
        client=None,
    )

    cancel_order_transaction = await Transaction.cancel_order(
        address="owner_address", symbol="pair", refid="", testnet=True, client=None
    )

    freeze_token_transaction = await Transaction.freeze_token(
        address="ownder_address", symbol="token", amount=1, testnet=True, client=None
    )

    unfreeze_token_tranasaction = await Transaction.unfreeze_token_transaction(
        address="ownder_address", symbol="token", amount=1, testnet=True, client=None
    )

    vote_transaction = await Transaction.vote_transaction(
        voter, proposal_id, option=Votes.YES, client=None, testnet=True
    )

    issue_token_transaction = await Transaction.issue_token_transaction(
        owner, name, symbol, sypply, mintable, client=None, testnet=True
    )

    mint_token_transaction = await Transaction.mint_token_transaction(
        owner, symbol, amount, client=None, testnet=True
    )

    burn_token_transaction = Transaction.burn_token_transaction(
        owner, symbol, amount, client=None, testnet=True
    )

    """
    Get Sign Message to sign with wallet
    """
    sign_message_bytes_format = limit_buy_transaction.get_sign_message()
