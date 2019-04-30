# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
    Create and manage Transactions
"""
from typing import Union, Any, Tuple, Optional, List, Dict
from decimal import Decimal
from .httpclient import HTTPClient
from .enums import Ordertype, Side, Timeinforce, Votes
from .transaction_base import TransactionBase

TESTNET_CHAIN_ID = "Binance-Chain-Nile"
MAINNET_CHAIN_ID = "Binance-Chain-Tigris"

number_type = Union[str, float, int, Decimal]


class Transaction:
    @staticmethod
    async def new_order_transaction(
        address: str,
        symbol: str,
        side: Side,
        price: number_type,
        quantity: number_type,
        ordertype: Ordertype = Ordertype.LIMIT,
        timeInForce: Timeinforce = Timeinforce.GTE,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """ Create New Order TransactionBase object"""
        transaction = await Transaction.prepare_transaction(
            address=address,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
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
        transaction = await Transaction.prepare_transaction(
            address=address,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
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
        transaction = await Transaction.prepare_transaction(
            address=from_address,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
        )
        transaction.get_transfer_msg(
            to_address=to_address, symbol=symbol, amount=amount
        )
        return transaction

    @staticmethod
    async def multi_transfer_transaction(
        from_address: str,
        to_address: str,
        transfers: List[Dict[str, number_type]],
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """
            Create transfer Transaction Base object
        """
        transaction = await Transaction.prepare_transaction(
            address=from_address,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
        )
        transaction.get_multi_transfer_msg(to_address=to_address, transfers=transfers)
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
        transaction = await Transaction.prepare_transaction(
            address=address,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
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
        transaction = await Transaction.prepare_transaction(
            address=address,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
        )
        transaction.get_unfreeze_token_msg(symbol=symbol, amount=amount)
        return transaction

    @staticmethod
    async def vote_transaction(
        voter: str,
        proposal_id: Union[int, str],
        option: Votes,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
        client: Any = None,
    ) -> TransactionBase:
        """
        Create vote TransactionBase object
        """
        transaction = await Transaction.prepare_transaction(
            address=voter,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
        )
        transaction.get_vote_msg(proposal_id=proposal_id, option=option)
        return transaction

    @staticmethod
    async def issue_token_transaction(
        owner: str,
        name: str,
        symbol: str,
        supply: int,
        mintable: bool,
        client: Any = None,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
    ):
        transaction = await Transaction.prepare_transaction(
            address=owner,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
        )
        transaction.get_issue_msg(
            name=name, symbol=symbol, supply=supply, mintable=mintable
        )
        return transaction

    @staticmethod
    async def mint_token_transaction(
        owner: str,
        symbol: str,
        amount: number_type,
        client: Any = None,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
    ):
        transaction = await Transaction.prepare_transaction(
            address=owner,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
        )
        transaction.get_mint_msg(symbol=symbol, amount=amount)
        return transaction

    @staticmethod
    async def burn_token_transaction(
        owner: str,
        symbol: str,
        amount: number_type,
        client: Any = None,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
    ):
        transaction = await Transaction.prepare_transaction(
            address=owner,
            client=client,
            testnet=testnet,
            account_number=account_number,
            sequence=sequence,
        )
        transaction.get_burn_msg(symbol=symbol, amount=amount)
        return transaction

    @staticmethod
    async def prepare_transaction(
        address: str,
        client: Any = None,
        testnet: bool = False,
        account_number: int = None,
        sequence: int = None,
    ):
        if not client:
            client = HTTPClient(testnet=testnet)
            chain_id = TESTNET_CHAIN_ID if testnet else MAINNET_CHAIN_ID
        else:
            chain_id = TESTNET_CHAIN_ID if client._testnet else MAINNET_CHAIN_ID
        account_info = await client.get_account(address)
        if not account_info:
            account_number = account_number if account_number else 0
            sequence = sequence if sequence else 0
        else:
            account_number = account_info["account_number"]
            sequence = account_info["sequence"]
        transaction = TransactionBase(
            address=address,
            account_number=account_number,
            sequence=sequence,
            chainid=chain_id,
        )
        return transaction

    def __init__(self, wallet: Any, client: Any = None, testnet: bool = False):
        self.wallet = wallet
        self.address = wallet.get_address()
        if not client:
            self.client = HTTPClient(testnet=testnet)
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
        side: Side,
        ordertype: Ordertype,
        price: number_type,
        quantity: number_type,
        timeInForce: Timeinforce,
    ) -> Any:
        """
            Create,sign and broadcast new_order tranasction
        """
        account_number, sequence = await self.get_account_info()
        transaction = await Transaction.new_order_transaction(
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
        transaction = await Transaction.cancel_order_transaction(
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
        transaction = await Transaction.transfer_transaction(
            from_address=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            to_address=to_address,
            symbol=symbol,
            amount=amount,
        )
        return await self.sign_and_broadcast(transaction)

    async def multi_transfer(
        self, to_address: str, transfers: List[Dict[str, number_type]]
    ) -> Any:
        """Create, sign and broadcast transfer transaction"""
        account_number, sequence = await self.get_account_info()
        transaction = await Transaction.multi_transfer_transaction(
            from_address=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            to_address=to_address,
            transfers=transfers,
        )
        return await self.sign_and_broadcast(transaction)

    async def freeze_token(self, symbol: str, amount: number_type) -> Any:
        """Create, sign and broadcast free_token transaction"""
        account_number, sequence = await self.get_account_info()
        transaction = await Transaction.freeze_token_transaction(
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
        transaction = await Transaction.unfreeze_token_transaction(
            address=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            symbol=symbol,
            amount=amount,
        )
        return await self.sign_and_broadcast(transaction)

    async def vote(self, proposal_id: str, option: Votes):
        account_number, sequence = await self.get_account_info()
        transaction = await Transaction.vote_transaction(
            voter=self.address,
            client=self.client,
            account_number=account_number,
            sequence=sequence,
            proposal_id=proposal_id,
            option=option,
        )
        return await self.sign_and_broadcast(transaction)

    async def issue_token(self, name: str, symbol: str, supply: int, mintable: bool):
        account_number, sequence = await self.get_account_info()
        transaction = await Transaction.issue_token_transaction(
            client=self.client,
            owner=self.address,
            name=name,
            symbol=symbol,
            supply=supply,
            mintable=mintable,
        )
        return await self.sign_and_broadcast(transaction)

    async def mint_token(self, symbol: str, amount: number_type):
        account_number, sequence = await self.get_account_info()
        transaction = await Transaction.mint_token_transaction(
            client=self.client, owner=self.address, symbol=symbol, amount=amount
        )
        return await self.sign_and_broadcast(transaction)

    async def burn_token(self, symbol: str, amount: number_type):
        account_number, sequence = await self.get_account_info()
        transaction = await Transaction.burn_token_transaction(
            client=self.client, owner=self.address, symbol=symbol, amount=amount
        )
        return await self.sign_and_broadcast(transaction)

    async def sign_and_broadcast(self, transaction: TransactionBase) -> Any:
        """Sign and broadcast an TransactionBase object"""
        pub, sig = self.wallet.sign(transaction.get_sign_message())
        hex_data = transaction.update_signature(pub, sig)
        broadcast_info = await self.client.broadcast(hex_data)
        return broadcast_info
