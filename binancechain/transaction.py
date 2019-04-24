"""
    Create and manage wallets
"""
import aiohttp
from .httpclient import BinanceChain
from bitcoinlib import encoding
from .crypto import generate_id
import numpy as np
import simplejson

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
        symbol: str,
        side: int,
        price: float,
        quantity: float,
        sequence=None,
        timeInForce: int = 1,
        testnet: bool = False,
        memo: str = "",
        account_number: int = None,
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
            print(account_info)
            account_number = account_info["account_number"]
        if not sequence:
            sequence = account_info["sequence"]
            sequence += 1
        tx = BinanceTransaction(
            testnet=testnet,
            memo=memo,
            type="NewOrder",
            account_number=account_number,
            sequence=sequence,
        )
        id = generate_id(address, sequence)
        tx.update_msg(
            {
                "sender": address,
                "id": id,
                "ordertype": 2,  # currently only 1 type : limit =2, will change in the future
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
        self,
        memo,
        type,
        testnet=False,
        account_number=0,
        sequence=0,
        chain_id=CHAIN_ID,
        data=[],
    ):
        self.testnet = testnet
        self.account_number = account_number
        self.sequence = sequence
        self.memo = memo
        self.data = data
        self.type = type
        self.StdSignMsg = {
            "memo": memo,
            "msgs": [],
            "account_number": account_number,
            "sequence": sequence,
            "chain_id": chain_id,
            "source": "1",
        }

    def update_msg(self, msg):
        self.msg = msg
        self.StdSignMsg["msgs"].append(msg)

    def update_signature(self, pubkey, signature):
        self.stdSignature = {
            "account_number": self.account_number,
            "sequence": self.sequence,
            "pubkey": pubkey,
            "signature": signature,
        }
        self.StdTx = {
            "msgs": [self.msg],
            "signature": [self.stdSignature],
            "memo": self.memo,
            "data": self.data,
            "source": "1",
        }
        stdTxBytes = bytes(simplejson.dumps(self.StdTx, sort_keys=True), "utf-8")
        stdTxBytes = TYPE_PREFIX[self.type] + stdTxBytes
        lenBytes = np.uint64(len(stdTxBytes)).tobytes()
        self.txblob = (lenBytes + stdTxBytes).hex()
