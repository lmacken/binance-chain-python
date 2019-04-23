"""
    Create and manage wallets
"""
import aiohttp
from .httpclient import BinanceChain

CHAIN_ID = "chain-bnb"
TYPE_PREFIX = {
    "CancelOrder": 0x166E681B,
    "TokenFreeze": 0xE774B32D,
    "TokenUnfreeze": 0x6515FF0D,
    "NewOrder": 0xCE6DC043,
    "Send": 0x2A2C87FA,
    "PubKey": 0xEB5AE987,
    "StdTx": 0xF0625DEE,
}
TX_TYPE = {
    "MsgSend": "MsgSend",
    "NewOrderMsg": "NewOrderMsg",
    "CancelOrderMsg": "CancelOrderMsg",
    "StdTx": "StdTx",
    "PubKeySecp256k1": "PubKeySecp256k1",
    "SignatureSecp256k1": "SignatureSecp256k1",
}


class BinanceTransaction:
    @staticmethod
    async def new_order(
        address,
        symbol,
        side: int,
        price,
        quantity,
        sequence=None,
        timeInForce=1,
        testnet=False,
        memo="",
        account_number=None,
    ):
        """
            Return Transaction NewOrderMsg including sequence and account number, ready to be signed
        """
        # todo assert vars
        binance_chain = BinanceChain(testnet=testnet)
        if not account_number:
            account_info = await binance_chain.get_account(address)
            if not account_info:
                raise Exception("No account information found")
            account_number = account_info["result"]["account_number"]
        if not sequence:
            sequence = await binance_chain.get_account_sequence(address)
            sequence += 1
        tx = BinanceTransaction(
            testnet=testnet,
            memo=memo,
            type=TX_TYPE["NewOrderMsg"],
            account_number=account_number,
            sequence=sequence,
        )
        id = f"{address.to_hex()}-{sequence}"  # fixme string to hex
        tx.update(
            {
                "sender": address,
                "id": id,
                "orderType": 2,  # currently only 1 type : limit =2, will change in the future
                "symbol": symbol,
                "side": side,
                "price": price,
                "quantity": quantity,
                "timeinforce": timeInForce,
            }
        )
        return tx

    @staticmethod
    def cancel_order():
        pass

    @staticmethod
    def transfer():
        pass

    @staticmethod
    def free_token():
        pass

    @staticmethod
    def unfreze_token():
        pass

    def __init__(
        self, memo, type, testnet=False, account_number=0, sequence=0, chain_id=CHAIN_ID
    ):
        self.type = type
        self.memo = memo
        self.testnet = testnet
        self.msgs = []
        self.account_number = account_number
        self.sequence = sequence
        self.chain_id = chain_id

    def update(self, msg):
        self.msgs.append(msg)
