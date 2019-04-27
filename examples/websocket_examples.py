#!/usr/bin/env python3

from pprint import pprint

import binancechain

address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"

dex = binancechain.WebSocket(address, testnet=True)


def on_open():
    dex.subscribe_user_orders(callback=user_orders)
    dex.subscribe_user_accounts(callback=user_accounts)
    dex.subscribe_user_transfers(callback=user_transfers)


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
