import json


class Message(object):

    message_type: str

    def to_json(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return self.to_json()

    def _asdict(self):
        return self.__dict__
