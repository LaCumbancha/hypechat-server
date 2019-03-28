import unittest

from models import Message


class MessageTestCase(unittest.TestCase):
    def test_create(self):
        new_message = Message(sender='Juan', receiver='Pedro', text_content='Hola!')
        self.assertEquals(new_message.sender(), 'Juan')
        self.assertEquals(new_message.receiver(), 'Pedro')
        self.assertEquals(new_message.text_content(), 'Hola!')
