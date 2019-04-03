from app import db


class Message(db.Model):
    __tablename__ = 'messages'

    _id = db.Column(name='id', type_=db.Integer, primary_key=True)
    _sender = db.Column(name='sender', type_=db.String(), nullable=False)
    _receiver = db.Column(name='receiver', type_=db.String(), nullable=False)
    _text_content = db.Column(name='text_content', type_=db.String(), nullable=False)

    @classmethod
    def new_with(cls, sender, receiver, text_content):
        new_message = Message(sender=sender, receiver=receiver, text_content=text_content)
        db.session.add(new_message)
        db.session.commit()

        return new_message

    def __init__(self, sender, receiver, text_content):
        self.sender = sender
        self.receiver = receiver
        self.text_content = text_content

    def sender(self):
        return self._sender

    def receiver(self):
        return self._receiver

    def text_content(self):
        return self._text_content
