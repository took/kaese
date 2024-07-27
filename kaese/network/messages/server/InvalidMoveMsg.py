from kaese.network.messages.Message import Message


class InvalidMoveMsg(Message):
    def __init__(self, error_message: str):
        self.message_type = 'InvalidMoveMsg'
        self.error_message = error_message
