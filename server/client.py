import bh_message.bh_message
from util.helper import log

from websockets.asyncio.client import ClientConnection
from dataclasses import dataclass

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
        for client in self.clients:
            if (client != sender):
                await client.push(text)

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
        self.name: str = "anon" # TODO
        self.room: Room = None

    def register(self):
        if self.room != None:
            self.room.register(self)
    def unregister(self):
        if self.room != None:
            self.room.unregister(self)

    async def broadcast(self, text: str):
        if self.room != None:
            await self.room.broadcast(self, text)
        pass

    def switch_room(self, new_room: Room):
        self.unregister()
        self.room = new_room
        self.register()

    async def push(self, text: str):
        await self.conn.send(text)

    async def handle_message(self, input: str):
        message = bh_message.bh_message.from_json(input)
        if message is None: return

        match message.type:
            case 'text': await self.broadcast(message.body)
            case 'join':
                room_name = message.body
                try:
                    room = Room.get_room(room_name)
                except KeyError:
                    return
                self.switch_room(room)
            case 'create':
                room = Room.add_room(message.body)
                self.switch_room(room)
