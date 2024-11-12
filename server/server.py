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

def create_database():
    """
    1. connect to the database
    2. Check if table 'message' exist
    3. If it does, exit
    4. Otherwise, create it
    """
    import sqlite3
    import os.path
    from pathlib import Path

    app_dir = os.path.expanduser("~/.bunnyhop") 
    path = Path(app_dir)
    if not path.exists():
        path.mkdir(parents=True)

    con = sqlite3.connect(f'{app_dir}/storage')
    cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='message';")
    if res.fetchone() is None:
        cur.execute("""CREATE TABLE message(
            sender TEXT,
            message TEXT,
            room TEXT,
            time_stamp TEXT
            )""")
    con.close()

async def run():
    create_database()
    async with serve(handler, "", 8080, ping_interval=10, ping_timeout=20):
        await asyncio.get_running_loop().create_future() # run forever