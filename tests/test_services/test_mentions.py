import unittest
from unittest.mock import MagicMock

'''Mocking environment properties'''
import sys
sys.modules["daos.database"] = MagicMock()
sys.modules["daos.messages"] = MagicMock()

from dtos.models.messages import UserMention, ChannelMention
from services.mentions import MentionService
from sqlalchemy.exc import IntegrityError

mock = MagicMock()


class MockedMentionsDatabase:

    batch_mentions = []
    saved_mentions = []


class AuthenticationTestCase(unittest.TestCase):

    def setUp(self) -> None:
        MockedMentionsDatabase.batch_mentions = []
        MockedMentionsDatabase.saved_mentions = []

    def test_saving_mentions_save_one_for_each_mentioned_user(self):
        message = MagicMock()
        message.message_id = 0
        mentions = [0, 1, 2, 3, 4, 5]

        def add_mention(mention):
            from tests.test_services import test_facebook
            MockedMentionsDatabase.batch_mentions += [mention]

        def commit():
            from tests.test_services import test_facebook
            MockedMentionsDatabase.saved_mentions = MockedMentionsDatabase.batch_mentions
            MockedMentionsDatabase.batch_mentions = []

        sys.modules["daos.messages"].MessageDatabaseClient.add_mention = MagicMock(side_effect=add_mention)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)

        MentionService.save_mentions(message, mentions)
        self.assertEqual(len(mentions), len(MockedMentionsDatabase.saved_mentions))
        self.assertEqual(0, len(MockedMentionsDatabase.batch_mentions))

    def test_saving_mentions_throwing_integrity_exception_rollback_and_add_no_mention(self):
        message = MagicMock()
        message.message_id = 0
        mentions = [0, 1, 2, 3, 4, 5]

        def add_mention(mention):
            from tests.test_services import test_facebook
            MockedMentionsDatabase.batch_mentions += [mention]

        def commit():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_facebook
            MockedMentionsDatabase.batch_mentions = []

        sys.modules["daos.messages"].MessageDatabaseClient.add_mention = MagicMock(side_effect=add_mention)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=commit)
        sys.modules["daos.database"].DatabaseClient.rollback = MagicMock(side_effect=rollback)

        MentionService.save_mentions(message, mentions)
        self.assertEqual(0, len(MockedMentionsDatabase.saved_mentions))
        self.assertEqual(0, len(MockedMentionsDatabase.batch_mentions))

    def test_getting_user_mentions_works_properly(self):
        mocked_mentions = [ChannelMention(channel_id=0, channel_name="TEST")]

        sys.modules["daos.messages"].MessageDatabaseClient.get_mentions_by_message.return_value = mocked_mentions

        output_mentions = MentionService.get_mentions(0)
        self.assertTrue(len(mocked_mentions), len(output_mentions))
        self.assertEqual(output_mentions[0].get("type"), "CHANNEL")
        self.assertIsNotNone(output_mentions[0].get("name"))

    def test_getting_channel_mentions_works_properly(self):
        mocked_mentions = [UserMention(user_id=0, username="TEST", first_name="TEST", last_name="TEST")]

        sys.modules["daos.messages"].MessageDatabaseClient.get_mentions_by_message.return_value = mocked_mentions

        output_mentions = MentionService.get_mentions(0)
        self.assertTrue(len(mocked_mentions), len(output_mentions))
        self.assertEqual(output_mentions[0].get("type"), "USER")
        self.assertIsNotNone(output_mentions[0].get("username"))
        self.assertIsNotNone(output_mentions[0].get("first_name"))
        self.assertIsNotNone(output_mentions[0].get("last_name"))

    def test_getting_mixed_mentions_works_properly(self):
        mocked_mentions = [
            ChannelMention(channel_id=0, channel_name="TEST"),
            UserMention(user_id=0, username="TEST", first_name="TEST", last_name="TEST")
        ]

        sys.modules["daos.messages"].MessageDatabaseClient.get_mentions_by_message.return_value = mocked_mentions

        output_mentions = MentionService.get_mentions(0)
        self.assertTrue(len(mocked_mentions), len(output_mentions))
        self.assertEqual(output_mentions[0].get("type"), "CHANNEL")
        self.assertEqual(output_mentions[1].get("type"), "USER")
        self.assertIsNotNone(output_mentions[0].get("name"))
        self.assertIsNotNone(output_mentions[1].get("username"))
        self.assertIsNotNone(output_mentions[1].get("first_name"))
        self.assertIsNotNone(output_mentions[1].get("last_name"))
