#!/usr/bin/env python

from util import helper
from server.client import handle_new_client

import asyncio
from websockets.asyncio.server import serve

async def handler(websocket):
    remote = websocket.remote_address
    helper.log(f"Received connection from: {remote}")
    await handle_new_client(websocket)
    helper.log(f"Remote {remote} disconnected")

async def run():
    async with serve(handler, "", 8080):
        await asyncio.get_running_loop().create_future() # run forever