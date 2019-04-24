#!/usr/bin/env python3

from pprint import pprint

from binancechain import BinanceChainWebSocket

dex = BinanceChainWebSocket(testnet=True)


def on_open():
    dex.subscribe_all_tickers(callback=tickers)


def tickers(msg):
    pprint(msg)


def user_orders(msg):
    print(f"user_orders: {msg}")


def user_accounts(msg):
    print(f"user_accounts: {msg}")


def user_transfers(msg):
    print(f"user_transfers: {msg}")


def mini_tickers(msg):
    print(f"mini_tickers: {msg}")


def on_error(msg):
    print(f"Error: {msg}")


if __name__ == '__main__':
    try:
        dex.start(on_open, on_error)
    except KeyboardInterrupt:
        dex.close()
