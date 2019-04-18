#!/usr/bin/env python3
# Copyright 2019 Sensei.Chat
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
"""
Binance DEX CLI
"""
import argparse
import asyncio
from functools import update_wrapper
from pprint import pprint

import click
import pandas as pd

from binancechain import BinanceChain


def run(coro):
    """ Run an async coroutine """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


def dex_run(method, **kwargs):
    """ Run a method on the Binance DEX client """
    dex = BNC()
    result = run(getattr(dex, method)(**kwargs))
    pprint(result)
    run(dex.close())
    return result


@click.group()
def main():
    pass


@main.command()
def time():
    dex_run("get_time")


@main.command()
def node_info():
    dex_run("get_node_info")


@main.command()
def fees():
    dex_run("get_fees")


@main.command()
def validators():
    dex_run("get_validators")


@main.command()
def peers():
    dex_run("get_peers")


@main.command()
def tokens():
    dex_run("get_token_list")


@main.command()
def markets():
    dex_run("get_markets")


@main.command()
@click.argument("symbol")
def depth(**kwargs):
    dex_run("get_depth", **kwargs)


@main.command()
@click.argument("hash")
def broadcast(**kwargs):
    dex_run("broadcast", **kwargs)


@main.command()
@click.argument("symbol")
@click.argument("interval")
def klines(**kwargs):
    dex_run("get_klines", **kwargs)


@main.command()
@click.option("--address", help="the seller/buyer address", type=str)
@click.option("--end", help="end time in milliseconds", type=int)
@click.option("--limit", help="default 50; max 1000.", type=int)
@click.option("--offset", help="start with 0; default 0.", type=int)
@click.option("--side", help="order side. 1 for buy and 2 for sell.", type=int)
@click.option("--start", help="start time in milliseconds", type=int)
@click.option(
    "--status",
    help="order status list. Allowed value: [Ack, PartialFill, IocNoFill, FullyFill, Canceled, Expired, FailedBlocking, FailedMatching]",
    type=str,
)
@click.option("--symbol", help="symbol", type=str)
@click.option(
    "--total",
    help="total number required, 0 for not required and 1 for required; default not required, return total=-1 in response",
    type=int,
)
def closed_orders(**kwargs):
    dex_run("get_closed_orders", **kwargs)


@main.command()
@click.option("--address", help="the seller/buyer address", type=str)
@click.option("--limit", help="default 50; max 1000.", type=int)
@click.option("--offset", help="start with 0; default 0.", type=int)
@click.option("--symbol", help="symbol", type=str)
@click.option(
    "--total",
    help="total number required, 0 for not required and 1 for required; default not required, return total=-1 in response",
    type=int,
)
def open_orders(**kwargs):
    dex_run("get_open_orders", **kwargs)


@main.command()
@click.argument("symbol", default="")
def ticker(**kwargs):
    dex_run("get_ticker", **kwargs)


@main.command()
@click.option("--address", help="the seller/buyer address")
@click.option("--end", help="end time", type=int)
@click.option("--limit", help="default 50; max 1000.", type=int)
@click.option("--offset", help="start with 0; default 0.", type=int)
@click.option("--start", help="start time", type=int)
@click.option(
    "--total",
    help="total number required, 0 for not required and 1 for required; default not required, return total=-1 in response",
    type=int,
)
def trades(**kwargs):
    dex_run("get_trades", **kwargs)


@main.command()
@click.option("--address", help="the seller/buyer address")
@click.option("--end", help="end time", type=int)
@click.option("--limit", help="default 50; max 1000.", type=int)
@click.option("--offset", help="start with 0; default 0.", type=int)
@click.option("--start", help="start time", type=int)
@click.option(
    "--total",
    help="total number required, 0 for not required and 1 for required; default not required, return total=-1 in response",
    type=int,
)
def block_exchange_fee(**kwargs):
    dex_run("get_block_exchange_fee", **kwargs)


@main.command()
@click.argument("address")
@click.option("--height", help="block height", type=int)
@click.option("--end", help="end in milliseconds", type=int)
@click.option("--limit", help="default 50; max 1000.", type=int)
@click.option("--offset", help="start with 0; default 0.", type=int)
@click.option(
    "--side", help="transaction side. Allowed value: [ RECEIVE, SEND]", type=str
)
@click.option("--start", help="start time in milliseconds", type=int)
@click.option("--tx-asset", help="txAsset", type=str)
@click.option(
    "--tx-type",
    help="transaction type. Allowed value: [NEW_ORDER,ISSUE_TOKEN,BURN_TOKEN,LIST_TOKEN,CANCEL_ORDER,FREEZE_TOKEN,UN_FREEZE_TOKEN,TRANSFER,PROPOSAL,VOTE,MINT,DEPOSIT]",
    type=str,
)
def transactions(**kwargs):
    dex_run("get_transactions", **kwargs)


if __name__ == "__main__":
    main()
