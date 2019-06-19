import unittest
from unittest.mock import MagicMock

'''Mocking environment properties'''
import sys

sys.modules["daos.database"] = MagicMock()
sys.modules["daos.messages"] = MagicMock()

from services.mentions import MentionService


class AuthenticationTestCase(unittest.TestCase):

    saved_mentions = []

    def test_saving_mentions_save_one_for_each_mentioned_user(self):
        message = MagicMock()
        message.message_id = 0
        mentions = [0, 1, 2, 3, 4, 5]

        def save_mentions(mention):
            from tests.services import test_facebook
            AuthenticationTestCase.saved_mentions += [mention]

        sys.modules["daos.messages"].MessageDatabaseClient.add_mention = MagicMock(side_effect=save_mentions)

        MentionService.save_mentions(message, mentions)
        self.assertEquals(len(mentions), len(self.saved_mentions))
