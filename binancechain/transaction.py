"""
    Create and manage wallets
"""
import aiohttp
from .httpclient import BinanceChain
from bitcoinlib import encoding
from .crypto import generate_id
import numpy as np
import simplejson
import marshal
from varint import encode
import binascii
from .transaction_pb2 import (
    NewOrder,
    CancelOrder,
    Send,
    Freeze,
    Unfreeze,
    Vote,
    StdSignature,
    PubKey,
)

SOURCE = "1"
CHAIN_ID = "chain-bnb"
TYPE_PREFIX = {
    "CancelOrder": "166E681B",
    "TokenFreeze": "E774B32D",
    "TokenUnfreeze": "6515FF0D",
    "NewOrder": "CE6DC043",
    "Send": "2A2C87FA",
    "PubKey": "EB5AE987",
    "StdTx": "F0625DEE",
    "Vote": "A1CADD36",
}
MSG_TYPES = {
    "CancelOrder": CancelOrder,
    "TokenFreeze": Freeze,
    "TokenUnfreeze": Unfreeze,
    "NewOrder": NewOrder,
    "Send": Send,
    "Vote": Vote,
}

TESTNET_CLIENT = BinanceChain(testnet=True)
CLIENT = BinanceChain(testnet=False)


class BinanceTransaction:
    @staticmethod
    async def new_order(
        address,
        symbol,
        side,
        price,
        quantity,
        ordertype=1,
        timeInForce=1,
        testnet=False,
    ):
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account(address)
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address, account_number=account_number, sequence=sequence
        )
        return transaction.create_new_order(
            symbol=symbol,
            side=side,
            ordertype=ordertype,
            price=price,
            quantity=quantity,
            timeinforce=timeInForce,
        )

    @staticmethod
    async def cancel_order(address, testnet=False):
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account(address)
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address, account_number=account_number, sequence=sequence
        )
        return transaction.create_new_order(
            symbol=symbol,
            side=side,
            ordertype=ordertype,
            price=price,
            quantity=quantity,
            timeinforce=timeInForce,
        )

    @staticmethod
    async def send(address, testnet=False):
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account()
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address, account_number=account_number, sequence=sequence
        )
        return transaction.create_new_order(
            symbol=symbol,
            side=side,
            ordertype=ordertype,
            price=price,
            quantity=quantity,
            timeinforce=timeInForce,
        )

    @staticmethod
    async def vote(address, testnet=False):
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account()
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address, account_number=account_number, sequence=sequence
        )
        return transaction.create_new_order(
            symbol=symbol,
            side=side,
            ordertype=ordertype,
            price=price,
            quantity=quantity,
            timeinforce=timeInForce,
        )

    def __init__(self, address, account_number, sequence):
        self.account_number = account_number
        self.address = address
        self.sequence = sequence
        self.StdSignMsg = json.loads(
            json.dumps(
                {
                    "memo": "",
                    "msgs": [],
                    "account_number": account_number,
                    "sequence": sequence,
                    "chain_id": CHAIN_ID,
                    "source": SOURCE,
                },
                sort_keys=True,
            )
        )

    def create_new_order(
        self, symbol, side, price, quantity, ordertype=1, timeInForce=1, sequence=None
    ):
        id = generate_id(self.address, self.sequence)
        price = int(Decimal(price) * BASE)
        quantity = int(Decimal(quantity) * Decimal(100000000))
        self.msg = {
            "symbol": symbol,
            "sender": self.address,
            "id": id,
            "side": side,
            "ordertype": ordertype,
            "timeinforce": timeInForce,
            "price": price,
            "quantity": quantity,
        }
        self.StdSignMsg["msgs"].append(self.msg)
        self.SignMessage = bytes(simplejson.dumps(msg, sort_keys=True), "utf-8")
        self.StdMsg = self.generate_std_neworder(self.msg)
        return self.SignMessage

    def generate_std_neworder(self, msg):
        std = NewOrder()
        std.sender = self.address
        std.id = generate_id(self.address, self.sequence)
        std.ordertype: msg[
            "ordertype"
        ]  # currently only 1 type : limit =2, will change in the future
        std.symbol = msg["symbol"]
        std.side = msg["side"]
        std.price = msg["price"]
        std.quantity = msg["quantity"]
        std.timeinforce = msg["timeinforce"]
        proto_bytes = std.serializeToString()
        type_bytes = binascii.unhexlify(encoding.to_bytes(TYPE_PREFIX["NewOrder"]))
        return type_bytes + proto_bytes

    def get_sign_message(self):
        return self.SignMessage

    def update_signature(self, pubkey, signature):
        print("SIGNATURE", pubkey, signature)
        pubkey_bytes = pubkey_to_msg(pubkey)
        self.stdSignature = self.generate_stdSignature(pubkey_bytes, signature)
        self.stdTx = self.generate_StdTx()
        return self.stdTx

    def pubkey_to_msg(self, pubkey, signature):
        key_bytes = encoding.to_bytes(pubkey)
        return (
            binascii.unhexlify(encoding.to_bytes(TYPE_PREFIX["PubKey"]))
            + varint_encode(len(key_bytes))
            + key_bytes
        )

    def generate_stdSignature(self, pubkey_bytes, signature):
        std = StdSignature()
        std.account_number = self.account_number
        std.sequence = self.sequence
        std.signature = signature
        std.pub_key = pubkey_bytes
        proto_bytes = std.SerializeToString()
        return encode(len(proto_bytes)) + proto_bytes

    def generate_StdTx(self):
        std = StdTx()
        std.data = self.data
        std.memo = self.memo
        std.source = self.source
        std.signatures.extend([self.stdSignature])
        std.msgs.extend([self.stdMsg])
        proto_bytes = std.serializeToString()
        type_bytes = binascii.unhexlify(TYPE_PREFIX["StdTx"])
        return encode(len(proto_bytes) + len(type_bytes)) + type_bytes + proto_bytes
