class ChatDTO:

    def __init__(self, username, token, receiver_id, text_content):
        self.username = username
        self.token = token
        self.receiver_id = receiver_id
        self.text_content = text_content
