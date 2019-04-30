#!/usr/bin/env python

import setuptools
from distutils.core import setup

setup(
    name="binancechain",
    version="0.1.6",
    description="Unofficial Binance Chain SDK",
    author="Luke Macken & Kim Bui",
    author_email="",
    url="https://github.com/lmacken/binance-chain-python",
    packages=["binancechain"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    install_requires=[
        "wheel",
        "bech32",
        "aiohttp",
        "bitcoinlib",
        "eth_keyfile",
        "secp256k1",
        "pyee",
        "varint",
        "protobuf",
        "orjson",
    ],
)
