from app import db

import logging


class MessageService:

    @classmethod
    def new_with(cls, sender, receiver, text_content):
        new_message = MessageTableEntry(sender=sender, receiver=receiver, text_content=text_content)
        db.session.add(new_message)
        db.session.commit()

        return new_message
