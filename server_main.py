#!/usr/bin/python

import server.server as server

import asyncio

if __name__ == "__main__":
    asyncio.run(server.run())