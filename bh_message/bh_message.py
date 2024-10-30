import json

class BHMessage:
    type: str
    body: str
    def __init__(self, type: str, body: str):
        self.body = body
        self.type = type

    def to_json(self) -> str:
        return json.dumps({'type': self.type, 'body': self.body})

    def from_json(self, text: str) -> None:
        message_json = json.loads(text)
        if 'type' in message_json:
            self.type = message_json['type']
        if 'body' in message_json:
            self.body = message_json['body']