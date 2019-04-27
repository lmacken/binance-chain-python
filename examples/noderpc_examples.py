from binancechain import NodeRPC


async def nodeRPC_examples():
    noderpc = NodeRPC(testnet=True)

    abic_info = await noderpc.get_abci_info(path, data=None, height="0", prove=False)

    concensus_state = await noderpc.get_consensus_state()

    dump_concensus_state = await noderpc.get_dump_consensus_state()

    genesis = await noderpc.get_genesis()

    health = await noderpc.get_health()

    net_info = await noderpc.get_net_info()

    status = await noderpc.get_status()

    query = await noderpc.abci_query("/param/fees")

    block = await noderpc.block(height=None)

    block_hash = await noderpc.block_by_hash(hash)

    block_results = await noderpc.block_results(height=None)  # ABCIResults

    blockchain = await noderpc.blockchain(min_height, max_height)

    concensus_params = await noderpc.consensus_params("1")

    validators = await noderpc.validators(height=None)

    transaction = await noderpc.tx(txid, prove=False)

    tx_search = await noderpc.tx_search(query, prove=False, page=1, per_page=30)

    pending_transactions = await noderpc.unconfirmed_txs(limit=None)

    pendings_number = await noderpc.get_num_unconfirmed_txs()

    tx_hash = await noderpc.broadcast_tx_async(hash)

    tx_onchain = await noderpc.broadcast_tx_sync(hash)

    tx_confirmed = await noderpc.commit(height=None)
