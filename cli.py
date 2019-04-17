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

from binancedex.httpclient import BNC


def run(coro):
    """ Run an async coroutine """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@click.group()
def main():
    pass


@main.command()
def time():
    dex = BNC()
    time = run(dex.get_time())
    pprint(time)
    run(dex.close())


@main.command()
def node_info():
    dex = BNC()
    info = run(dex.get_node_info())
    pprint(info)
    run(dex.close())


@main.command()
def fees():
    dex = BNC()
    fees = run(dex.get_fees())
    pprint(fees)
    run(dex.close())


@main.command()
def validators():
    dex = BNC()
    validators = run(dex.get_validators())
    pprint(validators)
    run(dex.close())


@main.command()
def peers():
    dex = BNC()
    peers = run(dex.get_peers())
    pprint(peers)
    run(dex.close())


@main.command()
def tokens():
    dex = BNC()
    tokens = run(dex.get_token_list())
    pprint(tokens)
    run(dex.close())


@main.command()
def markets():
    dex = BNC()
    markets = run(dex.get_markets())
    pprint(markets)
    run(dex.close())


@main.command()
@click.argument('symbol')
def depth(symbol):
    dex = BNC()
    depth = run(dex.get_depth(symbol))
    pprint(depth)
    run(dex.close())



if __name__ == '__main__':
    main()
