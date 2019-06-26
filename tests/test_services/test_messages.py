import unittest
from unittest.mock import MagicMock

'''Mocking environment properties'''
import sys
sys.modules["daos.users"] = MagicMock()
sys.modules["daos.teams"] = MagicMock()
sys.modules["daos.channels"] = MagicMock()
sys.modules["daos.messages"] = MagicMock()
sys.modules["daos.database"] = MagicMock()
sys.modules["services.mentions"] = MagicMock()
sys.modules["services.notifications"] = MagicMock()
sys.modules["models.authentication"] = MagicMock()
sys.modules["logging"].getLogger = MagicMock()

from services.messages import MessageService

mock = MagicMock()


class MessagesServiceTestCase(unittest.TestCase):

    def tearDown(self):
        pass
