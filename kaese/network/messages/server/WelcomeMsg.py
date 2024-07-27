from kaese.network.messages.Message import Message


class WelcomeMsg(Message):
    def __init__(self):
        self.message_type = 'WelcomeMsg'
