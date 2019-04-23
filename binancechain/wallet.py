"""
    Intergrate with different methods of signing
"""

from eth_keyfile import *
from bitcoinlib import keys, mnemonic, encoding
from .crypto import from_path, get_address

HDPATH = "44'/714'/0'/0/0"


class BinanceWallet:
    def __init__(self, testnet=False):
        self.testnet = testnet
        self.prefix = "tbnb" if testnet else "bnb"

    def set_privatekey(self, privatekey):
        self.privatekey = privatekey
        self.address = self.privatekey.public_key.address(testnet=self.testnet)

    def create_wallet(self, password=""):
        root_key = keys.HDKey(password=password)
        self.key = from_path(root_key=root_key, path=HDPATH)
        self.address = get_address(prefix=self.prefix, key=self.key)
        return {"privateKey": self.key.private_hex, "address": self.address}

    def create_wallet_keystore(self, password=""):
        m = mnemonic.Mnemonic()
        mnem = m.generate(256)
        root_key = keys.HDKey.from_seed(m.to_seed(mnem, password=password))
        self.key = from_path(root_key=root_key, path=HDPATH)
        return create_keyfile_json(
            private_key=self.key.private_byte, password=bytes(password, "utf-8")
        )

    def create_wallet_mnemonic(self, language="english", password=""):
        m = mnemonic.Mnemonic(language)
        mnem = m.generate(256)
        root_key = keys.HDKey.from_seed(m.to_seed(mnem, password=password))
        self.key = from_path(root_key=root_key, path=HDPATH)
        self.address = get_address(prefix=self.prefix, key=self.key)
        return {"privateKey": self.key.private_hex, "address": self.address}

    def recover_from_keystore(self, keystore, password=""):
        private_key = decode_keyfile_json(
            keystore, password=encoding.to_bytes(password)
        )
        print(private_key)
        self.key = keys.HDKey(private_key)
        self.address = get_address(prefix=self.prefix, key=self.key)
        return {"privateKey": self.key.private_hex, "address": self.address}

    def recover_from_privatekey(self, privatekey):
        self.key = keys.HDKey(import_key=privatekey)
        self.address = get_address(prefix=self.prefix, key=self.key)
        return {"privateKey": self.key.private_hex, "address": self.address}

    def recover_from_mnemonic(self, words):
        m = mnemonic.Mnemonic(language="english")
        root_key = keys.HDKey.from_seed(m.to_seed(words=words))
        self.key = from_path(root_key=root_key, path=HDPATH)
        self.address = get_address(prefix=self.prefix, key=self.key)
        return {"privateKey": self.key.private_hex, "address": self.address}

    def get_address(self):
        if not self.address:
            raise Exception("Wallet is not initiated")
        return self.address

    def sign_data(self):
        pass


if __name__ == "__main__":
    # m = Mnemonic("english").generate(256)
    m = "tennis utility midnight pattern that foot security tent punch glance still night virus loop trade velvet rent glare ramp cushion defy grass section cage"
    bn = BNWallet(testnet=True)
    key_store = bn.create_wallet_keystore()
    print(key_store)
    wallet = bn.recover_from_keystore(keystore=key_store)
    print(wallet)
