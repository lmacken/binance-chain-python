Implementation Details
----------------------

- Python3 asyncio
- asyncio
- aiohttp
    connection pooling?

REST HTTP Client
Node RPC Client
Wallet
Transaction Builder

WebSocket
  - `aiohttp <https://aiohttp.readthedocs.io>` powered
  - Event-driven, using `pyee <https://github.com/jfhbrook/pyee>`
  - Decorator API for simple usage
  - Automatically sends `keepAlive` messages every 30 minutes


SDK features
------------
    - CLI
    - Rate limiter (TODO)


Best Practices
--------------
- Extensive pytest suite
- SPDX license identifiers
- Python3.6+ f-strings
- Type annotations
- Exception-chaining with `raise from`
- Consistent syntax formatting with `Black <https://github.com/ambv/black>`


Running the test suite
----------------------

    `git clone ...`
    `pip install -r test-requirements.txt`
    `python setup.py develop`
    `pytest -v --cov=binancechain`


Using the REST API
------------------

Using the Node API
------------------

Using the WebSocket
-------------------

Using the Wallet
----------------
