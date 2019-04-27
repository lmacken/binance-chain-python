from binancechain import HTTPClient


async def http_examples():
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

    """ POST REQUEST"""
    broadcast_info = await client.broadcast(data)
