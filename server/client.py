from server.message import Message
from server.room import Room
from server.room import get_room
from server.room import add_room
from util.helper import log
from bh_message.bh_message import BHMessage

import json
from websockets.asyncio.client import ClientConnection

class Client:
    conn: ClientConnection
    room: Room
    name: str

    def __init__(self, conn: ClientConnection):
        self.conn = conn
        name = "anon" # TODO
        room = None

    def register(self):
        if self.room != None:
            self.room.register(self)

    def unregister(self):
        if self.room != None:
            self.room.unregister(self)

    def broadcast(self, text: str):
        if self.room != None:
            self.room.broadcast(Message(self, text))
        pass

    def switch_room(self, new_room: Room):
        self.unregister()
        self.room = new_room
        self.register()

    async def push(self, message: Message):
        await self.conn.send(message.content)

    async def read(self):
        async for message in self.conn:
            remote = self.conn.remote_address
            log(f'[{remote}]: {message}')
            self.handle_message(message)

    def handle_message(self, input: str):
        message = BHMessage()
        message.from_json(input)

        match message.type:
            case 'text': self.broadcast(message.body)
            case 'join':
                room_name = message.body
                try:
                    room = get_room(room_name)
                except KeyError:
                    return
                self.switch_room(room)
            case 'create':
                room = add_room(message.body)
                self.switch_room(room)

async def handle_new_client(websocket: ClientConnection):
    log(f'Received connection: {websocket.remote_address}')
    new_client = Client(websocket)
    # we could extract self.conn from server.client.Client entirely
    # and run the 'async for ...' in here
    await new_client.read()
    pass