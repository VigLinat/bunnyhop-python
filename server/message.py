from dataclasses import dataclass
from server.client import Client

@dataclass
class Message:
    sender: Client
    content: str