import json
from typing import Optional

class BHMessage:
    def __init__(self, type: str, body: str):
        self.body: str = body
        self.type: str = type

def to_json(bh_message: BHMessage) -> str:
    return json.dumps({'type': bh_message.type, 'body': bh_message.body})

def from_json(json_str: str) -> Optional[BHMessage]:
    json_dict = json.loads(json_str)
    type = json_dict['type']
    body = json_dict['body']
    return BHMessage(type, body) if type is not None and body is not None else None
