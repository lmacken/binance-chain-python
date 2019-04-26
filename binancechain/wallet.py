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
    def create_wallet_privatekey(privatekey, testnet=False):
        key = keys.HDKey(import_key=privatekey)
        return BinanceWallet(key=key, testnet=testnet)

    @staticmethod
    def create_wallet(password="", testnet=False):
        root_key = keys.HDKey(passphrase=password)
        key = from_path(root_key=root_key, path=HDPATH)
        return BinanceWallet(key=key, testnet=testnet)

    @staticmethod
    def create_wallet_keystore(password=""):
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
        return BinanceWallet(key=key, testnet=testnet)

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
    def recover_from_mnemonic(words, testnet=False):
        m = mnemonic.Mnemonic(language="english")
        root_key = keys.HDKey.from_seed(m.to_seed(words=words))
        key = from_path(root_key=root_key, path=HDPATH)
        return BinanceWallet(key=key, testnet=testnet)

    def __init__(self, key, testnet=False):
        self.testnet = testnet
        self.prefix = TESTNET_PREFIX if testnet else MAINET_PREFIX
        self.key = key
        self.address = get_address(prefix=self.prefix, key=key)

    def get_address(self):
        if not self.address:
            raise Exception("Wallet is not initiated")
        return self.address

    def get_privatekey(self):
        if not self.key:
            raise Exception("Wallet is not initiated")
        return self.key.private_hex

    def sign(self, msg):
        """
            Return signature
        """
        priv = PrivateKey(self.key.private_byte)
        sig = priv.ecdsa_sign(msg)
        h = priv.ecdsa_serialize_compact(sig)
        return self.key.public_byte, h
        # sig = keys.sign(msg, self.key)
        # print("SIGNATURE", sig.as_bytes, sig.as_hex)
        # return self.key.public_byte, sig.as_der_encoded[-64:]

    def verify_signature(self, msg, signature):
        pass
