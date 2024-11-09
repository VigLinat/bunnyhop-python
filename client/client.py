import bh_message
import bh_message.bh_message
import util.helper as helper

import sys
import asyncio
import re

from websockets.asyncio.client import connect

remote = "ws://127.0.0.1:8080"

async def ainput(string: str = None) -> str:
    loop = asyncio.get_event_loop()
    if string is not None: await loop.run_in_executor(None, lambda: sys.stdout.write(string+' '))
    return await loop.run_in_executor(None, input)

async def send_user_input(websocket):
    while True:
        try:
            input = await ainput()
            message = parseUserInput(input)
            await websocket.send(message)
        except EOFError:
            helper.log(f"Closing connection to remote: {remote}")
            await websocket.close()
            break;

async def listen_to_server(websocket):
    async for message in websocket:
        print(message)

async def run():
    helper.log(f"Connecting to remote: {remote}")
    async with connect(remote, ping_interval=10, ping_timeout=20) as websocket:
        read_task = asyncio.create_task(send_user_input(websocket))
        listen_task = asyncio.create_task(listen_to_server(websocket))
        await read_task
        await listen_task

commandRegex = re.compile(r"^#(?P<cmd>\w+) (?P<body>\w+)")
def parseUserInput(input: str) -> str:
    match = commandRegex.match(input)
    if match is None:
        cmd = "text"
        body = input
    else:
        cmd = match.group(1)
        body = match.group(2)
    message = bh_message.bh_message.BHMessage(cmd, body)
    return bh_message.bh_message.to_json(message)
