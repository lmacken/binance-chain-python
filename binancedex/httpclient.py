"""
    Interact with binance chain
"""
import datetime

import aiohttp

NETWORK_PREFIX_MAPPING = {"testnet": "tbnb", "mainnet": "bnb"}
API = [
    "time",
    "node-info",
    "validators",
    "peers",
    "account",
    "tx",
    "tokens",
    "markets",
    "fees",
    "depth",
    "broadcast",
    "klines",
    "orders",
    "ticker",
    "trades",
    "transactions",
]

TEST_URL = "https://testnet-dex.binance.org/api/v1/time"
URL = TEST_URL


class BNC:
    def __init__(self, testnet=False, session=None):
        url = URL if not testnet else TEST_URL
        self.server = url + "/api/v1"
        self.session = aiohttp.ClientSession()

    def set_network(self, network):
        self.network = network

    async def get_request(self, _uri, params=None):
        async with self.session.get(self.server + uri, params=params) as resp:
            json_body = await resp.json()
            return json_body

    async def post_request(self, _uri, data=None):
        async with self.session.post(self.server + uri, data=data) as resp:
            return resp

    async def get_balance(self, _address):
        try:
            info = await self.get_account_info(_address)
            return info["result"]["balance"]
        except:
            return "No balance found"

    async def get_account_info(self, _address):
        uri = "/account/" + _address
        return self.get_request(uri)

    async def get_time(self):
        return self.get_request("/time")

    async def get_node_info(self):
        return self.get_request("/node-info")

    async def get_validators(self):
        return self.get_request("/validators")

    async def get_peers(self):
        return self.get_request("/peers")

    async def get_transaction(self, _txid):
        return self.get_request("/tx/" + _txid)

    async def get_token_list(self):
        return self.get_request("/tokens")

    async def get_markets(self, _limit=500, _offset=0):
        params = {"limit": _limit, "offset": _offset}
        return self.get_request("/tokens/", params=params)

    async def get_fees(self):
        return self.get_request("/fees")

    async def get_depth(self, symbol, limit=100):
        params = {"symbol": symbol, "limit": limit}
        return self.get_request("/depth", params=params)

    async def broadcast(self, _signedTx):
        return self.post_request("/broadcast", data=_signedTx)

    async def get_klines(
        self, symbol, interval, limit=300, startTime=None, endTime=None
    ):
        return self.get_request(
            "/klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
                "startTime": startTime,
                "endTime": endTime,
            },
        )

    async def get_closed_orders(
        self,
        address,
        end=None,
        limit=None,
        offset=None,
        side=None,
        start=None,
        status=None,
        symbol=None,
        total=None,
    ):
        params = {
            "address": address,
            "end": end,
            "limit": limit,
            "offset": offset,
            "side": side,
            "start": start,
            "status": status,
            "symbol": symbol,
            "total": total,
        }
        return self.get_request("/orders/closed", params=params)

    async def get_open_orders(
        self, address, limit=None, offset=None, symbol=None, total=None
    ):
        prms = {
            "address": address,
            "limit": limit,
            "offset": offset,
            "symbol": symbol,
            "total": total,
        }
        return self.get_request("/orders/open", params=prms)

    async def get_orders_by_id(self, id):
        return self.get_request("/orders/" + id)

    async def get_ticker(self, symbol=None):
        prms = {"symbol": symbol}
        return self.get_request("/ticker/24hr", params=prms)

    async def get_trades(
        self,
        address=None,
        buyerOrderId=None,
        height=None,
        limit=None,
        offset=None,
        quoteAsset=None,
        sellerOrderId=None,
        side=None,
        start=None,
        end=None,
        total=None,
        symbol=None,
    ):
        prms = {
            "address": address,
            "buyerOrderId": buyerOrderId,
            "height": height,
            "limit": limit,
            "offset": offset,
            "sellerOrderId": sellerOrderId,
            "side": side,
            "start": start,
            "end": end,
            "symbol": symbol,
            "total": total,
        }
        return self.get_request("/trades", params=prms)

    async def get_transactions(
        self,
        address,
        blockHeight,
        startTime,
        endTime,
        limit,
        offset,
        side,
        txAsset,
        txType,
    ):
        prms = {
            "address": address,
            "blockHeight": blockHeight,
            "startTime": startTime,
            "endTime": endTime,
            "limit": limit,
            "offset": offset,
            "side": side,
            "txAsset": txAsset,
            "txType": txType,
        }


async def main():
    bnc = BNC("testnet-dex.binance.org")
    time = bnc.get_time()
    print(time)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    loop.run_forever()
