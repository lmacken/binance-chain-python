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
def fees():
    dex = BNC()
    fees = run(dex.get_fees())
    pprint(fees)
    run(dex.close())


if __name__ == '__main__':
    main()
