from bitcoinlib import encoding
import bech32


def from_path(root_key, path):
    if isinstance(path, str):
        p = path.rstrip("/").split("/")
    elif isinstance(path, bytes):
        p = path.decode("utf-8").rstrip("/").split("/")
    else:
        p = list(path)
    key = root_key
    for i in p:
        if isinstance(i, str):
            hardened = i[-1] == "'"
            index = int(i[:-1], 0) | 0x80000000 if hardened else int(i, 0)
        else:
            index = i
        key = key.child_private(index, hardened=hardened)
    return key


def get_address(prefix, key):
    convert = encoding.convertbits(encoding.hash160(key.public_compressed_byte), 8, 5)
    address = bech32.bech32_encode(prefix, convert)
    return address


def generate_signature(key, data):
    pass


def verify_signature(data, signed_data, pubkey):
    pass
