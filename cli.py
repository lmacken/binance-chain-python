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
    dex_run('get_time')


@main.command()
def node_info():
    dex_run('get_node_info')


@main.command()
def fees():
    dex_run('get_fees')


@main.command()
def validators():
    dex_run('get_validators')


@main.command()
def peers():
    dex_run('get_peers')


@main.command()
def tokens():
    dex_run('get_token_list')


@main.command()
def markets():
    dex_run('get_markets')


@main.command()
@click.argument('symbol')
def depth(symbol):
    dex_run('get_depth', symbol=symbol)


if __name__ == '__main__':
    main()
