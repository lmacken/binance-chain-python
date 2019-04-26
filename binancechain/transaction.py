"""
    Create and manage wallets
"""
import binascii
import json
import simplejson
from bitcoinlib import encoding
from varint import encode
from decimal import Decimal
from .crypto import generate_id, address_decode
from .httpclient import BinanceChain
from .enums import *
from .transaction_pb2 import (
    CancelOrder,
    Freeze,
    NewOrder,
    Send,
    StdSignature,
    Unfreeze,
    Vote,
    StdTx,
    Input,
    Output,
    Token,
)

SOURCE = "1"
CHAIN_ID = "Binance-Chain-Nile"
TYPE_PREFIX = {
    "CancelOrder": b"166E681B",
    "TokenFreeze": b"E774B32D",
    "TokenUnfreeze": b"6515FF0D",
    "NewOrder": b"CE6DC043",
    "Send": b"2A2C87FA",
    "PubKey": b"EB5AE987",
    "StdTx": b"F0625DEE",
    "Vote": b"A1CADD36",
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
BASE = 100000000


class BinanceTransaction:
    @staticmethod
    async def new_order_transaction(
        address,
        symbol,
        side,
        price,
        quantity,
        ordertype=2,
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
        transaction.create_new_order(
            symbol=symbol,
            side=side,
            ordertype=ordertype,
            price=price,
            quantity=quantity,
            timeInForce=timeInForce,
        )
        return transaction

    @staticmethod
    async def cancel_order_transaction(address, symbol, refid, testnet=False):
        print(address, symbol, refid)
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account(address)
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address, account_number=account_number, sequence=sequence
        )
        transaction.cancel_order(symbol=symbol, refid=refid)
        return transaction

    @staticmethod
    async def transfer_transaction(
        from_address, to_address, token, amount, testnet=False
    ):
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account(from_address)
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address=from_address, account_number=account_number, sequence=sequence
        )
        transaction.transfer(to_address=to_address, token=token, amount=amount)
        return transaction

    @staticmethod
    async def freeze_token_transaction(address, symbol, amount, testnet=False):
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account(address)
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address=address, account_number=account_number, sequence=sequence
        )
        transaction.freeze_token(symbol=symbol, amount=amount)
        return transaction

    @staticmethod
    async def unfreeze_token_transaction(address, symbol, amount, testnet=False):
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account(address)
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address=address, account_number=account_number, sequence=sequence
        )
        transaction.unfreeze_token(symbol=symbol, amount=amount)
        return transaction

    @staticmethod
    async def vote_transaction(voter, proposal_id, option, testnet=False):
        client = TESTNET_CLIENT if testnet else CLIENT
        account_info = await client.get_account(voter)
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        transaction = BinanceTransaction(
            address=voter, account_number=account_number, sequence=sequence
        )
        transaction.vote(proposal_id=proposal_id, option=option)
        print("transaction here", transaction)
        return transaction

    def __init__(self, address, account_number, sequence, memo="", data=""):
        self.account_number = account_number
        self.data = data.encode()
        self.memo = memo
        self.address = address
        self.sequence = sequence
        self.StdSignMsg = {
            "memo": self.memo,
            "msgs": [],
            "account_number": str(self.account_number),
            "sequence": str(self.sequence),
            "chain_id": CHAIN_ID,
            "source": str(SOURCE),
            "data": None,
        }

    def create_new_order(
        self,
        symbol,
        side: SIDE,
        price,
        quantity,
        sequence=None,
        ordertype: ORDERTYPE = ORDERTYPE.Limit,
        timeInForce: TIMEINFORCE = TIMEINFORCE.GTE,
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
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        self.stdMsg = self.generate_stdNewOrderMsg(self.msg)
        return self.SignMessage

    def generate_stdNewOrderMsg(self, msg):
        std = NewOrder()
        std.sender = address_decode(self.address)
        std.id = generate_id(self.address, self.sequence)
        std.ordertype = msg[
            "ordertype"
        ]  # currently only 1 type : limit =2, will change in the future
        std.symbol = msg["symbol"].encode()
        std.side = msg["side"]
        std.price = msg["price"]
        std.quantity = msg["quantity"]
        std.timeinforce = msg["timeinforce"]
        proto_bytes = std.SerializeToString()
        type_bytes = encoding.to_bytes(TYPE_PREFIX["NewOrder"])
        return type_bytes + proto_bytes

    def cancel_order(self, symbol, refid):
        self.msg = {"sender": self.address, "symbol": symbol, "refid": refid}
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = CancelOrder()
        std.symbol = symbol
        std.sender = address_decode(self.address)
        std.refid = refid
        self.stdMsg = (
            encoding.to_bytes(TYPE_PREFIX["CancelOrder"]) + std.SerializeToString()
        )
        return self.SignMessage

    def transfer(self, to_address, token, amount):
        amount = int(Decimal(amount) * BASE)
        self.msg = {
            "inputs": [
                {"address": self.address, "coins": [{"denom": token, "amount": amount}]}
            ],
            "outputs": [
                {"address": to_address, "coins": [{"denom": token, "amount": amount}]}
            ],
        }
        self.StdSignMsg["msgs"] = [self.msg]

        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = Send()
        input = Input()
        output = Output()
        token_proto = Token()
        token_proto.amount = amount
        token_proto.denom = token.encode()
        input.address = address_decode(self.address)
        input.coins.extend([token_proto])
        output.address = address_decode(to_address)
        output.coins.extend([token_proto])
        std.inputs.extend([input])
        std.outputs.extend([output])
        print(std)
        self.stdMsg = encoding.to_bytes(TYPE_PREFIX["Send"]) + std.SerializeToString()
        return self.SignMessage

    def freeze_token(self, symbol, amount):
        amount = int(Decimal(amount) * BASE)
        self.msg = {"from": self.address, "symbol": symbol, "amount": amount}
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = Freeze()
        setattr(std, "from", address_decode(self.address))
        std.symbol = symbol
        std.amount = amount
        self.stdMsg = (
            encoding.to_bytes(TYPE_PREFIX["TokenFreeze"]) + std.SerializeToString()
        )
        return self.SignMessage

    def unfreeze_token(self, symbol, amount):
        amount = int(Decimal(amount) * BASE)
        self.msg = {"from": self.address, "symbol": symbol, "amount": amount}
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = Freeze()
        setattr(std, "from", address_decode(self.address))
        std.symbol = symbol
        std.amount = amount
        self.stdMsg = (
            encoding.to_bytes(TYPE_PREFIX["TokenUnfreeze"]) + std.SerializeToString()
        )
        return self.SignMessage

    def vote(self, proposal_id, option):
        self.msg = {
            "proposal_id": proposal_id,
            "voter": self.address,
            "option": option.value,
        }
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = Vote()
        std.voter = address_decode(self.address)
        std.proposal_id = proposal_id
        std.option = option.value
        print(std)
        print(self.SignMessage)
        self.stdMsg = encoding.to_bytes(TYPE_PREFIX["Vote"]) + std.SerializeToString()
        return self.SignMessage

    def get_sign_message(self):
        return self.SignMessage

    def update_signature(self, pubkey, signature):
        pubkey_bytes = self.pubkey_to_msg(pubkey, signature)
        self.stdSignature = self.generate_stdSignatureMsg(pubkey_bytes, signature)
        self.stdTx = self.generate_StdTxMsg()
        return binascii.hexlify(self.stdTx)

    def pubkey_to_msg(self, pubkey, signature):
        key_bytes = encoding.to_bytes(pubkey)
        return (
            encoding.to_bytes(TYPE_PREFIX["PubKey"])
            + encode(len(key_bytes))
            + key_bytes
        )

    def generate_stdSignatureMsg(self, pubkey_bytes, signature):
        std = StdSignature()
        std.pub_key = pubkey_bytes
        std.signature = encoding.to_bytes(signature)
        std.account_number = self.account_number
        std.sequence = self.sequence
        proto_bytes = std.SerializeToString()
        return proto_bytes

    def generate_StdTxMsg(self):
        std = StdTx()
        std.msgs.extend([self.stdMsg])
        std.signatures.extend([self.stdSignature])
        std.memo = self.memo
        std.source = 1
        std.data = self.data
        proto_bytes = std.SerializeToString()
        type_bytes = encoding.to_bytes(TYPE_PREFIX["StdTx"])
        return encode(len(proto_bytes) + len(type_bytes)) + type_bytes + proto_bytes
