# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT
"""
    Intergrate with different methods of signing
"""

from eth_keyfile import decode_keyfile_json, create_keyfile_json
from bitcoinlib import keys, mnemonic, encoding
from .crypto import from_path, get_address
from secp256k1 import PrivateKey, PublicKey


HDPATH = "44'/714'/0'/0/0"
TESTNET_PREFIX = "tbnb"
MAINET_PREFIX = "bnb"


class Wallet:
    @staticmethod
    def create_wallet(password: str = "", testnet: bool = False):
        """
        Create brand new wallet
        """
        root_key = keys.HDKey(passphrase=password)
        key = from_path(root_key=root_key, path=HDPATH)
        return Wallet(key=key, testnet=testnet)

    @staticmethod
    def create_keystore(password: str = "") -> dict:
        """
            Create Keystore object
        """
        m = mnemonic.Mnemonic()
        mnem = m.generate(256)
        root_key = keys.HDKey.from_seed(m.to_seed(mnem, password=password))
        key = from_path(root_key=root_key, path=HDPATH)
        return create_keyfile_json(
            private_key=key.private_byte, password=bytes(password, "utf-8")
        )

    @staticmethod
    def create_wallet_mnemonic(
        language: str = "english", password: str = "", testnet: bool = False
    ):
        """
        Create wallet with mnemonic in language
        """
        m = mnemonic.Mnemonic(language)
        mnem = m.generate(256)
        root_key = keys.HDKey.from_seed(m.to_seed(mnem, password=password))
        key = from_path(root_key=root_key, path=HDPATH)
        return Wallet(key=key, testnet=testnet, mnemonic=mnem)

    @staticmethod
    def wallet_from_keystore(keystore: dict, password: str = "", testnet: bool = False):
        "Recover Binance wallet from keystore"
        private_key = decode_keyfile_json(
            keystore, password=encoding.to_bytes(password)
        )
        key = keys.HDKey(private_key)
        return Wallet(key=key, testnet=testnet)

    @staticmethod
    def wallet_from_privatekey(
        privatekey: str, password: str = "", testnet: bool = False
    ):
        """Recover Binance Wallet from privatekey"""
        key = keys.HDKey(import_key=privatekey, passphrase=password)
        return Wallet(key=key, testnet=testnet)

    @staticmethod
    def wallet_from_mnemonic(words: str, password: str = "", testnet: bool = False):
        "Recover wallet from mnemonic"
        m = mnemonic.Mnemonic(language="english")
        root_key = keys.HDKey.from_seed(m.to_seed(words=words, password=password))
        key = from_path(root_key=root_key, path=HDPATH)
        return Wallet(key=key, testnet=testnet, mnemonic=words)

    # @staticmethod
    # def wallet_from_seed(seed, testnet=False):
    #     root_key = keys.HDKey.from_seed(seed)
    #     key = from_path(root_key=root_key, path=HDPATH)
    #     return Wallet(key=key, testnet=testnet, mnemonic=words)

    def __init__(self, key: str, testnet: bool = False, mnemonic: str = None):
        self.testnet = testnet
        self.prefix = TESTNET_PREFIX if testnet else MAINET_PREFIX
        self.key = key
        self.address = get_address(prefix=self.prefix, key=key)
        if mnemonic:
            self.mnemonic = mnemonic

    def get_address(self) -> str:
        """Return wallet's address"""
        return self.address

    def get_privatekey(self):
        """Return wallet's private key"""
        return self.key.private_hex

    def get_publickey(self):
        """Return wallet's public key"""
        return self.key.public_hex

    def get_mnemonic(self):
        if not self.mnemonic:
            raise Exception("No mnemonic available in this wallet")
        return self.mnemonic

    def sign(self, msg):
        """
            Sign a message with private key, Return signature
        """
        priv = PrivateKey(self.key.private_byte, raw=True)
        sig = priv.ecdsa_sign(msg)
        h = priv.ecdsa_serialize_compact(sig)
        return self.key.public_hex, encoding.to_hexstring(h)

    def verify_signature(self, msg, signature):
        """Verify message and signature if its from this wallet"""
        pub = PublicKey(self.key.public_byte, raw=True)
        sig = pub.ecdsa_deserialize_compact(encoding.to_bytes(signature))
        valid = pub.ecdsa_verify(msg, sig)
        return valid
