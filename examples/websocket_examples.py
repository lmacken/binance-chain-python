#!/usr/bin/env python3

from pprint import pprint

import binancechain

address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"

dex = binancechain.WebSocket(address, testnet=True)


def callback(msg):
    print(msg)


def on_open():
    symbols = ["BNB_BTC.B-918"]
    dex.subscribe_user_orders(callback=callback)
    dex.subscribe_user_accounts(callback=callback)
    dex.subscribe_user_transfers(callback=callback)
    dex.subscribe_trades(callback=callback, symbols=symbols)
    dex.subscribe_market_depth(callback=callback, symbols=symbols)
    dex.subscribe_market_diff(callback=callback, symbols=symbols)
    dex.subscribe_klines(callback=callback, symbols=symbols)
    dex.subscribe_ticker(callback=callback, symbols=symbols)
    dex.subscribe_all_tickers(callback=callback)
    dex.subscribe_mini_ticker(callback=callback, symbols=symbols)
    dex.subscribe_all_mini_tickers(callback=callback)
    dex.subscribe_blockheight(callback=callback)


def user_orders(msg):
    pprint(msg)


def user_accounts(msg):
    pprint(msg)


def user_transfers(msg):
    pprint(msg)


def on_error(msg):
    pprint(msg)


if __name__ == '__main__':
    try:
        dex.start(on_open, on_error)
    except KeyboardInterrupt:
        pass
    finally:
        dex.close()
