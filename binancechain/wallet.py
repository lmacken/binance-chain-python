"""
    Intergrate with different methods of signing
"""

from eth_keyfile import decode_keyfile_json, create_keyfile_json
from bitcoinlib import keys, mnemonic, encoding
from .crypto import from_path, get_address
from ecdsa import SigningKey, SECP256k1
from secp256k1 import PrivateKey
import simplejson
import hashlib


HDPATH = "44'/714'/0'/0/0"
TESTNET_PREFIX = "tbnb"
MAINET_PREFIX = "bnb"


class BinanceWallet:
    @staticmethod
    def create_wallet(password="", testnet=False):
        root_key = keys.HDKey(passphrase=password)
        key = from_path(root_key=root_key, path=HDPATH)
        return BinanceWallet(key=key, testnet=testnet)

    @staticmethod
    def create_keystore(password=""):
        m = mnemonic.Mnemonic()
        mnem = m.generate(256)
        root_key = keys.HDKey.from_seed(m.to_seed(mnem, password=password))
        key = from_path(root_key=root_key, path=HDPATH)
        return create_keyfile_json(
            private_key=key.private_byte, password=bytes(password, "utf-8")
        )

    @staticmethod
    def create_wallet_mnemonic(language="english", password="", testnet=False):
        m = mnemonic.Mnemonic(language)
        mnem = m.generate(256)
        root_key = keys.HDKey.from_seed(m.to_seed(mnem, password=password))
        key = from_path(root_key=root_key, path=HDPATH)
        return BinanceWallet(key=key, testnet=testnet, mnemonic=mnem)

    @staticmethod
    def recover_from_keystore(keystore, password="", testnet=False):
        private_key = decode_keyfile_json(
            keystore, password=encoding.to_bytes(password)
        )
        key = keys.HDKey(private_key)
        return BinanceWallet(key=key, testnet=testnet)

    @staticmethod
    def recover_from_privatekey(privatekey, testnet=False):
        key = keys.HDKey(import_key=privatekey)
        return BinanceWallet(key=key, testnet=testnet)

    @staticmethod
    def recover_from_mnemonic(words, password="", testnet=False):
        m = mnemonic.Mnemonic(language="english")
        root_key = keys.HDKey.from_seed(m.to_seed(words=words, password=password))
        key = from_path(root_key=root_key, path=HDPATH)
        return BinanceWallet(key=key, testnet=testnet, mnemonic=words)

    def __init__(self, key, mnemonic=None, testnet=False):
        self.testnet = testnet
        self.prefix = TESTNET_PREFIX if testnet else MAINET_PREFIX
        self.key = key
        self.address = get_address(prefix=self.prefix, key=key)
        self.mnemonic = mnemonic

    def get_address(self):
        return self.address

    def get_privatekey(self):
        return self.key.private_hex

    def get_publickey(self):
        return self.key.public_hex

    def get_mnemonic(self):
        if not self.mnemonic:
            raise Exception("No Mnemonic available for this wallet")
        else:
            return self.mnemonic

    def sign(self, msg):
        """
            Return signature
        """
        priv = PrivateKey(self.key.private_byte)
        sig = priv.ecdsa_sign(msg)
        h = priv.ecdsa_serialize_compact(sig)
        return self.key.public_hex, encoding.to_hexstring(h)

    def verify_signature(self, msg, signature):
        pass
