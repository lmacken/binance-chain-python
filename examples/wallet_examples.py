"""
Example to use BinanceWallet for keys, keystore, address management
"""

from binancechain import BinanceWallet

"""
Create wallet
"""
wallet = BinanceWallet.create_wallet(password="", testnet=False)

wallet = BinanceWallet.create_wallet_mnemonic(
    language="english", password="", testnet=False
)

"""
Create Keystore
"""
keystore = BinanceWallet.create_keystore(password=None)


"""
Initiate wallet
"""
wallet = BinanceWallet(key="HDKEY object", testnet=False)
"""
Get wallet Recover from key
"""

wallet = BinanceWallet.wallet_from_keystore(
    keystore=keystore, password="", testnet=False
)

wallat = BinanceWallet.wallet_from_mnemonic(
    words="mnemonic words", password="", testnet=False
)

wallet = BinanceWallet.wallet_from_privatekey(
    privatekey="private_key", password="", testnet=False
)

wallet = BinanceWallet.wallet_from_seed(seed="seed", testnet=False)

"""
Use wallet to get address, sign, verify message
"""

address = wallet.get_address()

private_key = wallet.get_privatekey()

public_key = wallet.get_publickey()

pubkey, signature = wallet.sign("message")

isValid = wallet.verify_signature("message", signature)
