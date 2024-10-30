#!/usr/bin/env python

import util.helper as helper
import asyncio
import fileinput
import sys

from websockets.asyncio.client import connect

remote = "ws://127.0.0.1:8080"

async def send_user_input(websocket):
    while True:
        try:
            testString = input()
            await websocket.send(testString)
        except EOFError:
            helper.log(f"Closing connection to remote: {remote}")
            await websocket.close()
            break;

async def listen_to_server(websocket):
    async for message in websocket:
        print(message)

async def run():
    helper.log(f"Connecting to remote: {remote}")
    async with connect(remote) as websocket:
        read_task = asyncio.create_task(send_user_input(websocket))
        listen_task = asyncio.create_task(listen_to_server(websocket))
        await listen_task
        await read_task