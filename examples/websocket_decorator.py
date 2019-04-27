#!/usr/bin/env python3
"""
An example of the event-driven decorator WebSocket API
"""

import binancechain

ADDRESS = "tbnb18d6rnpmkxzqv3767xaaev5zzn06p42nya8zu79"

dex = binancechain.WebSocket(ADDRESS, testnet=True)


@dex.on("open")
async def on_open():
    print("Binance Chain WebSocket open!")


@dex.on("allTickers", symbols=["$all"])
async def on_ticker(msg):
    print(f"tickers: {str(msg)[:75]}")


@dex.on("kline_1m", symbols=["000-0E1_BNB"])
async def on_kline(kline):
    print(f"kline: {str(kline)[:75]}")


@dex.on("orders")
async def user_orders(msg):
    print(msg)


@dex.on("accounts")
async def user_accounts(msg):
    print(msg)


@dex.on("transfers")
async def user_transfers(msg):
    print(msg)


@dex.on("error")
async def on_error(msg):
    print(msg)


if __name__ == "__main__":
    try:
        dex.start()
    except KeyboardInterrupt:
        pass
    finally:
        dex.close()
