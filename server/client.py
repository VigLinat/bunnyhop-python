import bh_message.bh_message
from util.helper import log

from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed
from dataclasses import dataclass
import hashlib
import time

import sqlite3
import os.path
import weakref

class Room:
    def __init__(self, name: str):
        self.name = name
        self.clients: set[Client] = set()

    def register(self, client: Client):
        self.clients.add(client)

    def unregister(self, client: Client):
        if (client in self.clients):
            self.clients.remove(client)

    async def broadcast(self, sender: Client, text: str):
        text_message = f'{sender.name}: {text}'
        db_manager.new_message(sender.name, text, self.name)
        for client in self.clients:
            if (client != sender): 
                await client.push(text_message)

    def get_room(name: str) -> Room:
        return Room._all_rooms[name]

    def add_room(name: str) -> Room:
        if name in Room._all_rooms:
            return Room._all_rooms[name]
        else:
            new_room = Room(name)
            Room._all_rooms[name] = new_room
            return new_room

Room._global_room = Room("global")
Room._all_rooms = {'global': Room._global_room}

class Client:
    def __init__(self, conn: ClientConnection):
        self.conn: ClientConnection = conn
        hashstr = hashlib.sha384(bytes(str(time.time()), 'latin-1'), usedforsecurity=False)
        self.name: str = f'anon{hashstr.hexdigest()[-5:]}'
        self.room: Room = None

    def register(self):
        if self.room != None:
            self.room.register(self)

    def unregister(self):
        if self.room != None:
            self.room.unregister(self)

    def switch_room(self, new_room: Room):
        self.unregister()
        self.room = new_room
        self.register()

    async def push(self, text: str):
        try:
            await self.conn.send(text)
        except ConnectionClosed:
            self.unregister()


    def handle_join_room(self, room_name: str):
        try:
            room = Room.get_room(room_name)
        except KeyError:
            return
        self.switch_room(room)

    def handle_create_room(self, room_name: str):
        room = Room.add_room(room_name)
        self.switch_room(room)

    async def handle_send_message(self, message: str):
        if self.room != None: await self.room.broadcast(self, message)

    async def handle_message(self, input: str):
        message = bh_message.bh_message.from_json(input)
        if message is None: return

        match message.type:
            case 'text': await self.handle_send_message(message.body)
            case 'join': self.handle_join_room(message.body)
            case 'create': self.handle_create_room(message.body)

class DatabaseManager:
    def __init__(self, db_string: str, userexpand = True):
        self.db_con = sqlite3.connect(os.path.expanduser(db_string) if userexpand else db_string)

    def new_message(self, sender_name: str, message: str, room_name: str):
        cur = self.db_con.cursor()
        cur.execute("INSERT INTO message VALUES(?, ?, ?, datetime('now'))", (sender_name, message, room_name))
        self.db_con.commit()

    def free(self):
        self.db_con.close()

db_manager = DatabaseManager("~/.bunnyhop/storage")
weakref.finalize(db_manager, DatabaseManager.free, db_manager)
