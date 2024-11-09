from util import helper
from server.client import Client

import asyncio
from websockets.asyncio.server import serve
from websockets.asyncio.client import ClientConnection

async def handler(websocket):
    remote = websocket.remote_address
    helper.log(f"Received connection from: {remote}")
    await handle_new_client(websocket)
    helper.log(f"Remote {remote} disconnected")

async def handle_new_client(websocket: ClientConnection):
    helper.log(f'Received connection: {websocket.remote_address}')
    new_client = Client(websocket)
    async for message in websocket:
        remote = websocket.remote_address
        helper.log(f'[{remote}]: {message}')
        await new_client.handle_message(message)

async def run():
    async with serve(handler, "", 8080, ping_interval=10, ping_timeout=20):
        await asyncio.get_running_loop().create_future() # run forever