"""
    Intergrate with different methods of signing
"""


class BNS:
    def __init__(self):
        pass

    def set_privatekey(self, _privatekey):
        self.privatekey = _privatekey

    def create_wallet_privatekey(self):
        pass

    def create_wallet_keystore(self, _pass):
        pass

    def create_wallet_mnemonic(self):
        pass

    def recover_from_keystore(self, _keystore, _pass):
        pass

    def recover_from_privatekey(self, _privatekey):
        pass

    def recover_from_mnemonic(self, _mnemonic):
        pass

    def get_address(self):
        pass

    def transfer(self):
        pass
