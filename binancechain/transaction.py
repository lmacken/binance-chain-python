"""
    Create and manage wallets
"""
import binascii
from typing import Union, Any, Tuple
import json
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

BASE = 100000000
number_type = Union[str, float, int, Decimal]


class BinanceTransaction:
    @staticmethod
    async def new_order_transaction(
        address: str,
        symbol: str,
        side: SIDE,
        price: number_type,
        quantity: number_type,
        ordertype: ORDERTYPE = ORDERTYPE.Limit,
        timeInForce: TIMEINFORCE = TIMEINFORCE.GTE,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """ Create New Order TransactionBase object"""
        if not client:
            client = BinanceChain(testnet=testnet)
        if not account_number or not sequence:
            account_info = await client.get_account(address)
            account_number = account_info["account_number"]
            sequence = account_info["sequence"]
        transaction = TransactionBase(
            address, account_number=account_number, sequence=sequence
        )
        transaction.get_new_order_msg(
            symbol=symbol,
            side=side,
            ordertype=ordertype,
            price=price,
            quantity=quantity,
            timeInForce=timeInForce,
        )
        return transaction

    @staticmethod
    async def cancel_order_transaction(
        address: str,
        symbol: str,
        refid: str,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """
            Create Cancel order TransactionBase object
        """
        if not client:
            client = BinanceChain(testnet=testnet)
        if not account_number or not sequence:
            account_info = await client.get_account(address)
            account_number = account_info["account_number"]
            sequence = account_info["sequence"]
        transaction = TransactionBase(
            address, account_number=account_number, sequence=sequence
        )
        transaction.get_cancel_order_msg(symbol=symbol, refid=refid)
        return transaction

    @staticmethod
    async def transfer_transaction(
        from_address: str,
        to_address: str,
        symbol: str,
        amount: number_type,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """
            Create transfer Transaction Base object
        """
        if not client:
            client = BinanceChain(testnet=testnet)
        if not account_number or not sequence:
            account_info = await client.get_account(from_address)
            account_number = account_info["account_number"]
            sequence = account_info["sequence"]
        transaction = TransactionBase(
            address=from_address, account_number=account_number, sequence=sequence
        )
        transaction.get_transfer_msg(
            to_address=to_address, symbol=symbol, amount=amount
        )
        return transaction

    @staticmethod
    async def freeze_token_transaction(
        address: str,
        symbol: str,
        amount: number_type,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """
        Create free_token TransactionBase object
        """
        if not client:
            client = BinanceChain(testnet=testnet)
        if not account_number or not sequence:
            account_info = await client.get_account(address)
            account_number = account_info["account_number"]
            sequence = account_info["sequence"]
        transaction = TransactionBase(
            address=address, account_number=account_number, sequence=sequence
        )
        transaction.get_freeze_token_msg(symbol=symbol, amount=amount)
        return transaction

    @staticmethod
    async def unfreeze_token_transaction(
        address: str,
        symbol: str,
        amount: number_type,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """
        Create unfreeze token TransactionBase object
        """
        if not client:
            client = BinanceChain(testnet=testnet)
        if not account_number or not sequence:
            account_info = await client.get_account(address)
            account_number = account_info["account_number"]
            sequence = account_info["sequence"]
        transaction = TransactionBase(
            address=address, account_number=account_number, sequence=sequence
        )
        transaction.get_unfreeze_token_msg(symbol=symbol, amount=amount)
        return transaction

    @staticmethod
    async def vote_transaction(
        voter: str,
        proposal_id: Union[int, str],
        option: VOTES,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """
        Create vote TransactionBase object
        """
        if not client:
            client = BinanceChain(testnet=testnet)
        if not account_number or not sequence:
            account_info = await client.get_account(voter)
            account_number = account_info["account_number"]
            sequence = account_info["sequence"]
        transaction = TransactionBase(
            address=voter, account_number=account_number, sequence=sequence
        )
        transaction.get_vote_msg(proposal_id=proposal_id, option=option)
        return transaction

    def __init__(self, wallet: Any, client: Any = None, testnet: bool = False):
        self.wallet = wallet
        self.address = wallet.get_address()
        if not client:
            self.client = BinanceChain(testnet=testnet)
        else:
            self.client = client

    async def get_account_info(self) -> Tuple[int, int]:
        """Get account number and current valid sequence number"""
        account_info = await self.client.get_account(self.address)
        account_number = account_info["account_number"]
        sequence = account_info["sequence"]
        return account_number, sequence

    async def create_new_order(
        self,
        symbol: str,
        side: SIDE,
        ordertype: ORDERTYPE,
        price: number_type,
        quantity: number_type,
        timeInForce: TIMEINFORCE,
    ) -> Any:
        """
            Create,sign and broadcast new_order tranasction
        """
        account_number, sequence = await self.get_account_info()
        transaction = await BinanceTransaction.new_order_transaction(
            address=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            symbol=symbol,
            side=side,
            ordertype=ordertype,
            price=price,
            quantity=quantity,
            timeInForce=timeInForce,
        )
        return await self.sign_and_broadcast(transaction)

    async def cancel_order(self, symbol: str, refid: str) -> Any:
        """Create, sign and broadcast cancel_order transaction"""
        account_number, sequence = await self.get_account_info()
        transaction = await BinanceTransaction.cancel_order_transaction(
            address=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            symbol=symbol,
            refid=refid,
        )
        return await self.sign_and_broadcast(transaction)

    async def transfer(self, to_address: str, symbol: str, amount: number_type) -> Any:
        """Create, sign and broadcast transfer transaction"""
        account_number, sequence = await self.get_account_info()
        transaction = await BinanceTransaction.transfer_transaction(
            from_address=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            to_address=to_address,
            symbol=symbol,
            amount=amount,
        )
        return await self.sign_and_broadcast(transaction)

    async def freeze_token(self, symbol: str, amount: number_type) -> Any:
        """Create, sign and broadcast free_token transaction"""
        account_number, sequence = await self.get_account_info()
        transaction = await BinanceTransaction.freeze_token_transaction(
            address=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            symbol=symbol,
            amount=amount,
        )
        return await self.sign_and_broadcast(transaction)

    async def unfreeze_token(self, symbol: str, amount: number_type) -> Any:
        """Create, sign and broadcast unfreeze_token transaction"""
        account_number, sequence = await self.get_account_info()
        transaction = await BinanceTransaction.unfreeze_token_transaction(
            address=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            symbol=symbol,
            amount=amount,
        )
        return await self.sign_and_broadcast(transaction)

    async def vote(self, proposal_id: str, option: VOTES):
        account_number, sequence = await self.get_account_info()
        transaction = await BinanceTransaction.vote_transaction(
            voter=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            proposal_id=proposal_id,
            option=option,
        )
        return await self.sign_and_broadcast(transaction)

    async def sign_and_broadcast(self, transaction: TransactionBase) -> Any:
        """Sign and broadcast an TransactionBase object"""
        pub, sig = self.wallet.sign(transaction.get_sign_message())
        hex_data = transaction.update_signature(pub, sig)
        broadcast_info = await self.client.broadcast(hex_data)
        return broadcast_info


class TransactionBase:
    def __init__(
        self,
        address: str,
        account_number: int,
        sequence: int,
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
            "chain_id": CHAIN_ID,
            "source": str(SOURCE),
            "data": None,
        }

    def get_new_order_msg(
        self,
        symbol: str,
        side: SIDE,
        price: number_type,
        quantity: number_type,
        sequence=None,
        ordertype: ORDERTYPE = ORDERTYPE.Limit,
        timeInForce: TIMEINFORCE = TIMEINFORCE.GTE,
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

    def get_vote_msg(self, proposal_id: str, option: VOTES):
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

    def get_sign_message(self):
        return self.SignMessage

    def update_signature(self, pubkey: str, signature: str) -> bytes:
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
