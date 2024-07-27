from kaese.network.messages.Message import Message


class KeepAliveMsg(Message):
    def __init__(self):
        self.message_type = 'KeepAliveMsg'
