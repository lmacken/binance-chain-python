#!/usr/bin/env python3
"""
An example of the event-driven decorator WebSocket API
"""

from pprint import pprint

from binancechain import BinanceChainWebSocket

ADDRESS = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"

dex = BinanceChainWebSocket(ADDRESS, testnet=True)


@dex.on("open")
def on_open():
    print("Binance Chain WebSocket open!")


@dex.on("allTickers", symbols=["$all"])
def on_ticker(msg):
    print(f"tickers: {str(msg)[:75]}")


@dex.on("kline_1m", symbols=["000-0E1_BNB"])
def on_kline(kline):
    print(f"kline: {str(kline)[:75]}")


@dex.on("orders", address=ADDRESS)
def user_orders(msg):
    pprint(msg)


@dex.on("accounts", address=ADDRESS)
def user_accounts(msg):
    pprint(msg)


@dex.on("transfers", address=ADDRESS)
def user_transfers(msg):
    pprint(msg)


@dex.on("error")
def on_error(msg):
    pprint(msg)


if __name__ == "__main__":
    try:
        dex.start()
    except KeyboardInterrupt:
        pass
    finally:
        dex.close()
