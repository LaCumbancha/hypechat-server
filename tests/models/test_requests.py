import unittest

from models.request import ClientRequest


class ClientRequestTestCase(unittest.TestCase):

    def test_new_user_data_without_username(self):
        request = Object
        request.headers = []
        new_message = Message(sender='Juan', receiver='Pedro', text_content='Hola!')
        self.assertEqual(new_message.sender, 'Juan')
        self.assertEqual(new_message.receiver, 'Pedro')
        self.assertEqual(new_message.text_content, 'Hola!')
