import unittest
from unittest.mock import MagicMock

from dtos.models.messages import UserMention, ChannelMention, BotMention
from models.constants import SendMessageType
from sqlalchemy.exc import IntegrityError

'''Mocking environment properties'''
import sys
sys.modules["daos.bots"] = MagicMock()
sys.modules["daos.database"] = MagicMock()
sys.modules["daos.messages"] = MagicMock()
sys.modules["services.bots"] = MagicMock()
sys.modules["services.notifications"] = MagicMock()
sys.modules["logging"].getLogger = MagicMock()

from services.mentions import MentionService
mock = MagicMock()


class MockedMentionsDatabase:

    batch_mentions = []
    saved_mentions = []


class MentionServiceTestCase(unittest.TestCase):

    def tearDown(self):
        MockedMentionsDatabase.batch_mentions = []
        MockedMentionsDatabase.saved_mentions = []

    def test_saving_mentions_save_one_for_each_mentioned_user(self):
        message = MagicMock()
        message.message_id = 0
        message.send_type = SendMessageType.CHANNEL.value
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

    def test_saving_mentions_for_direct_channel_to_regular_user_works_properly(self):
        message = MagicMock()
        message.message_id = 0
        message.send_type = SendMessageType.DIRECT.value
        mentions = [0]

        def add_mention(mention):
            from tests.test_services import test_facebook
            MockedMentionsDatabase.batch_mentions += [mention]

        def commit():
            from tests.test_services import test_facebook
            MockedMentionsDatabase.saved_mentions = MockedMentionsDatabase.batch_mentions
            MockedMentionsDatabase.batch_mentions = []

        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = None
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

        def fail():
            raise IntegrityError(mock, mock, mock)

        def rollback():
            from tests.test_services import test_facebook
            MockedMentionsDatabase.batch_mentions = []

        sys.modules["daos.messages"].MessageDatabaseClient.add_mention = MagicMock(side_effect=add_mention)
        sys.modules["daos.database"].DatabaseClient.commit = MagicMock(side_effect=fail)
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

    def test_getting_bot_mentions_works_properly(self):
        mocked_mentions = [BotMention(bot_id=0, bot_name="TEST")]

        sys.modules["daos.messages"].MessageDatabaseClient.get_mentions_by_message.return_value = mocked_mentions

        output_mentions = MentionService.get_mentions(0)
        self.assertTrue(len(mocked_mentions), len(output_mentions))
        self.assertEqual(output_mentions[0].get("type"), "BOT")
        self.assertIsNotNone(output_mentions[0].get("name"))

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
