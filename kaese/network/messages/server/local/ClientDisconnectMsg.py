from kaese.network.messages.Message import Message


class ClientDisconnectMsg(Message):
    client_id: int
    error_message: str

    def __init__(self, client_id: int, error_message: str = ""):
        self.message_type = 'ClientDisconnectMsg'
        self.client_id = client_id
        self.error_message = error_message
