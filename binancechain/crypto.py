# Copyright 2019, Luke Macken, Kim Bui, and the binance-chain-python contributors
# SPDX-License-Identifier: MIT

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


def address_decode(address):
    prefix, words = bech32.bech32_decode(address)
    convert = encoding.convertbits(words, 5, 8)
    return bytes(convert)


def generate_signature(key, data):
    pass


def verify_signature(data, signed_data, pubkey):
    pass


def generate_id(address, sequence):
    prefix, words = bech32.bech32_decode(address)
    convert_w = encoding.convertbits(words, 5, 8)
    decodedAddress = encoding.to_bytearray(convert_w).hex()
    return f"{decodedAddress.upper()}-{sequence+1}"
