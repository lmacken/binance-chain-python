#!/usr/bin/env python3

from pprint import pprint

from binancechain import WebSocket

address = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"

dex = WebSocket(address, testnet=True)


def on_open():
    dex.subscribe_user_orders(address=address, callback=user_orders)
    dex.subscribe_user_accounts(address=address, callback=user_accounts)
    dex.subscribe_user_transfers(address=address, callback=user_transfers)


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
