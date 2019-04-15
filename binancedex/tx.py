"""
    Create and manage wallets
"""
import aiohttp


class BNW:
    def __init__(self, server):
        if not server:
            return "No Binance server found"
        self.session = aiohttp.ClientSession(server)

    def create_order(self):
        pass

    def cancel_order(self):
        pass
