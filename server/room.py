from server.client import Client
from server.message import Message

import asyncio

class Room:
    name: str
    clients: set[Client]
    def __init__(self, name: str):
        self.name = name

    def register(self, client: Client):
        self.clients.add(client)

    def unregister(self, client: Client):
        if (client in self.clients):
            self.clients.remove(client)

    def broadcast(self, message: Message):
        for client in self.clients:
            if (client != message.sender):
                client.push(message)

global_room = Room("global")

all_rooms = {'global': global_room}

def get_room(name: str) -> Room:
    return all_rooms['global']

def add_room(name: str) -> Room:
    if name in all_rooms:
        return all_rooms[name]
    else:
        new_room = Room(name)
        all_rooms[name] = new_room 
        return new_room
  