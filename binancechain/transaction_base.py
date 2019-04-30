import binascii
from typing import Union, Any, Tuple, Optional, List, Dict
import json
from bitcoinlib import encoding
from varint import encode
from decimal import Decimal
from .crypto import generate_id, address_decode
from .enums import Ordertype, Side, Timeinforce, Votes
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
    Issue,
    Mint,
    Burn,
)

SOURCE = "1"
TYPE_PREFIX = {
    "CancelOrder": b"166E681B",
    "TokenFreeze": b"E774B32D",
    "TokenUnfreeze": b"6515FF0D",
    "NewOrder": b"CE6DC043",
    "Send": b"2A2C87FA",
    "PubKey": b"EB5AE987",
    "StdTx": b"F0625DEE",
    "Vote": b"A1CADD36",
    "Issue": b"17EFAB80",
    "Mint": b"467E0829",
    "Burn": b"7ED2D2A0",
}

BASE = 100000000
number_type = Union[str, float, int, Decimal]


class TransactionBase:
    def __init__(
        self,
        address: str,
        account_number,
        sequence,
        chainid: str,
        memo: str = "",
        data: str = "",
    ):
        self.account_number = account_number
        self.data = data.encode()
        self.memo = memo
        self.address = address
        self.sequence = sequence
        self.StdSignMsg = {
            "memo": self.memo,
            "msgs": [dict],
            "account_number": str(self.account_number),
            "sequence": str(self.sequence),
            "chain_id": chainid,
            "source": str(SOURCE),
            "data": None,
        }
        print("CHAIN ID ", chainid)

    def get_new_order_msg(
        self,
        symbol: str,
        side: Side,
        price: number_type,
        quantity: number_type,
        sequence=None,
        ordertype: Ordertype = Ordertype.LIMIT,
        timeInForce: Timeinforce = Timeinforce.GTE,
    ):
        """Create new_order protobuf attributes, SignMessage of the transaction"""
        id = generate_id(self.address, self.sequence)
        price = int(Decimal(price) * BASE)
        quantity = int(Decimal(quantity) * Decimal(100000000))
        self.msg = {
            "symbol": symbol,
            "sender": self.address,
            "id": id,
            "side": side.value,
            "ordertype": ordertype.value,
            "timeinforce": timeInForce.value,
            "price": price,
            "quantity": quantity,
        }
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        self.stdMsg = self.generate_stdNewOrderMsg(self.msg)
        return self.SignMessage

    def generate_stdNewOrderMsg(self, msg: dict) -> bytes:
        """Generate StdMsg part of StdTx"""
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

    def get_cancel_order_msg(self, symbol: str, refid: str):
        """Generate cancel_order StdMsg for StdTx and SignMessage for current transaction"""
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

    def get_transfer_msg(self, to_address: str, symbol: str, amount: number_type):
        """Generate transfer StdMsg for StdTx and SignMessage for current transaction"""
        amount = int(Decimal(amount) * BASE)
        self.msg = {
            "inputs": [
                {
                    "address": self.address,
                    "coins": [{"denom": symbol, "amount": amount}],
                }
            ],
            "outputs": [
                {"address": to_address, "coins": [{"denom": symbol, "amount": amount}]}
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
        token_proto.denom = symbol.encode()
        input.address = address_decode(self.address)
        input.coins.extend([token_proto])
        output.address = address_decode(to_address)
        output.coins.extend([token_proto])
        std.inputs.extend([input])
        std.outputs.extend([output])
        self.stdMsg = encoding.to_bytes(TYPE_PREFIX["Send"]) + std.SerializeToString()
        return self.SignMessage

    def get_multi_transfer_msg(
        self, to_address: str, transfers: List[Dict[str, number_type]]
    ):
        """ Generate StdMsg and SignMessage for multiple tokens send in one transaction"""
        coins = []
        input = Input()
        output = Output()
        for transfer in transfers:
            coin = {}
            token = Token()
            amount = transfer["amount"]
            coin["denom"] = transfer["symbol"]
            coin["amount"] = token.amount = int(Decimal(amount) * BASE)
            token.denom = str(transfer["symbol"]).encode()
            coins.append(coin)
            input.coins.extend([token])
            output.coins.extend([token])
        self.msg = {
            "inputs": [{"address": self.address, "coins": coins}],
            "outputs": [{"address": to_address, "coins": coins}],
        }
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = Send()
        input.address = address_decode(self.address)
        output.address = address_decode(to_address)
        std.inputs.extend([input])
        std.outputs.extend([output])
        self.stdMsg = encoding.to_bytes(TYPE_PREFIX["Send"]) + std.SerializeToString()
        return self.SignMessage

    def get_freeze_token_msg(self, symbol: str, amount: number_type):
        """Generate freeze_token StdMsg for StdTx and SignMessage for current transaction"""
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

    def get_unfreeze_token_msg(self, symbol: str, amount: number_type):
        """Generate unfreeze_token StdMsg for StdTx and SignMessage for current transaction"""
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

    def get_vote_msg(self, proposal_id: Union[str, int], option: Votes):
        """Generate cancel_order StdMsg for StdTx and SignMessage for current transaction"""
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
        self.stdMsg = encoding.to_bytes(TYPE_PREFIX["Vote"]) + std.SerializeToString()
        return self.SignMessage

    def get_issue_msg(self, name: str, symbol: str, supply: int, mintable):
        """ Generate issue_token StdMsg and SignMessage"""
        self.msg = {
            "from": self.address,
            "name": name,
            "symbol": symbol,
            "total_supply": supply,
            "mintable": mintable,
        }
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = Issue()
        setattr(std, "from", address_decode(self.address))
        std.name = name
        std.symbol = symbol
        std.total_supply = int(supply)
        std.mintable = mintable
        self.stdMsg = encoding.to_bytes(TYPE_PREFIX["Issue"]) + std.SerializeToString()
        return self.SignMessage

    def get_mint_msg(self, symbol: str, amount: number_type):
        """ Generate mint_token StdMsg and SignMessage"""
        amount = int(Decimal(amount) * BASE)
        self.msg = {"from": self.address, "symbol": symbol, "amount": amount}
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = Mint()
        setattr(std, "from", address_decode(self.address))
        std.symbol = symbol
        std.amount = amount
        self.stdMsg = encoding.to_bytes(TYPE_PREFIX["Mint"]) + std.SerializeToString()
        return self.SignMessage

    def get_burn_msg(self, symbol: str, amount: number_type):
        """ Generate burn_token StdMsg and SignMessage"""
        amount = int(Decimal(amount) * BASE)
        self.msg = {"from": self.address, "symbol": symbol, "amount": amount}
        self.StdSignMsg["msgs"] = [self.msg]
        self.SignMessage = json.dumps(
            self.StdSignMsg, sort_keys=True, separators=(",", ":")
        ).encode()
        std = Burn()
        setattr(std, "from", address_decode(self.address))
        std.symbol = symbol
        std.amount = amount
        self.stdMsg = encoding.to_bytes(TYPE_PREFIX["Burn"]) + std.SerializeToString()
        return self.SignMessage

    def get_sign_message(self):
        return self.SignMessage

    def update_signature(self, pubkey: str, signature: str):
        """
        :Update current transaction with pubkey and signature from self.address
        :Create StdTx proto
        :Return data hex ready to be broadcast
        """
        pubkey_bytes = self.pubkey_to_msg(pubkey)
        self.stdSignature = self.generate_stdSignatureMsg(pubkey_bytes, signature)
        self.stdTx = self.generate_StdTxMsg()
        return binascii.hexlify(self.stdTx)

    def pubkey_to_msg(self, pubkey: str):
        key_bytes = encoding.to_bytes(pubkey)
        return (
            encoding.to_bytes(TYPE_PREFIX["PubKey"])
            + encode(len(key_bytes))
            + key_bytes
        )

    def generate_stdSignatureMsg(self, pubkey_bytes: bytes, signature: str):
        """Generate StdSignature for StdTx"""
        std = StdSignature()
        std.pub_key = pubkey_bytes
        std.signature = encoding.to_bytes(signature)
        std.account_number = self.account_number
        std.sequence = self.sequence
        proto_bytes = std.SerializeToString()
        return proto_bytes

    def generate_StdTxMsg(self):
        """Geneate StdTx"""
        std = StdTx()
        std.msgs.extend([self.stdMsg])
        std.signatures.extend([self.stdSignature])
        std.memo = self.memo
        std.source = 1
        std.data = self.data
        proto_bytes = std.SerializeToString()
        type_bytes = encoding.to_bytes(TYPE_PREFIX["StdTx"])
        return encode(len(proto_bytes) + len(type_bytes)) + type_bytes + proto_bytes

    def ___repr__(self):
        return "test string transaction"
