from kaese.network.messages.Message import Message


class ChatMsg(Message):
    def __init__(self, text, context='default'):
        self.message_type = 'ChatMsg'
        self.text = text
        self.context = context
