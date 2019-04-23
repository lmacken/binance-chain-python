"""
    Intergrate with different methods of signing
"""

from eth_keyfile import *
from bitcoinlib import keys, mnemonic, encoding
from .crypto import from_path, get_address

HDPATH = "44'/714'/0'/0/0"


class BinanceWallet:
    def create_wallet_privatekey(privatekey, testnet=False):
        key = keys.HDKey(import_key=privatekey)
        return BinanceWalet(key=key, testnet=testnet)

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
        self.prefix = "tbnb" if testnet else "bnb"
        self.key = key
        self.address = get_address(prefix=self.prefix, key=key)

    def get_address(self):
        if not self.address:
            raise Exception("Wallet is not initiated")
        return address

    def sign(self):
        pass

    def derive(self, path):
        pass


if __name__ == "__main__":
    # m = Mnemonic("english").generate(256)
    m = "tennis utility midnight pattern that foot security tent punch glance still night virus loop trade velvet rent glare ramp cushion defy grass section cage"
    bn = BinanceWallet.create_wallet(testnet=True)
    key_store = BinanceWallet.create_wallet_keystore()
    print(key_store)
    wallet = BinanceWallet.recover_from_keystore(keystore=key_store)
    print(wallet.address)
