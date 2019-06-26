import unittest
from unittest.mock import MagicMock

from dtos.models.users import PublicUser
from dtos.models.messages import *
from dtos.responses.messages import ChatsListResponse
from models.constants import TeamRoles, MessageResponseStatus
from datetime import datetime, timedelta

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

    def test_get_preview_messages_from_user_without_any_chats_return_empty_list(self):
        data = MagicMock()

        '''Mocked ouputs'''
        user = PublicUser(user_id=0)
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value
        direct_messages = []
        channel_messages = []

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.messages"].MessageDatabaseClient.get_direct_messages_previews.return_value = direct_messages
        sys.modules["daos.messages"].MessageDatabaseClient.get_channel_messages_previews.return_value = channel_messages

        response = MessageService.get_preview_messages(data)
        self.assertIsInstance(response, ChatsListResponse)
        self.assertEqual(0, len(response.chats))
        self.assertEqual(MessageResponseStatus.LIST.value, response.json().get("status"))

    def test_get_preview_messages_from_user_with_non_emtpy_chat_lists_work_proplery(self):
        data = MagicMock()

        '''Mocked ouputs'''
        user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value

        sender1 = UserMessageSender(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        direct1 = PreviewDirectMessage(message_id=0, sender=sender1, receiver_id=1, chat_name="Tester0", offset=1,
                                       content="Testeando1", message_type="TEXT", chat_online=False, chat_picture=None,
                                       timestamp=datetime.now() + timedelta(hours=-3))

        sender2 = BotMessageSender(bot_id=5, bot_name="Test-Bot")
        direct2 = PreviewDirectMessage(message_id=1, sender=sender2, receiver_id=0, chat_name="Test-Bot", offset=0,
                                       content="Testeando2", message_type="TEXT", chat_online=False, chat_picture=None,
                                       timestamp=datetime.now() + timedelta(hours=-2))

        sender3 = UserMessageSender(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        channel1 = PreviewChannelMessage(message_id=2, chat_id=3, chat_name="Channel-Test1", chat_picture=None,
                                         sender=sender3, content="Testeando3", message_type="TEXT", offset=0,
                                         timestamp=datetime.now() + timedelta(hours=-1))

        sender4 = BotMessageSender(bot_id=5, bot_name="Test-Bot")
        channel2 = PreviewChannelMessage(message_id=3, chat_id=4, chat_name="Channel-Test2", chat_picture=None,
                                         sender=sender4, content="Testeando4", message_type="TEXT", offset=0,
                                         timestamp=datetime.now() + timedelta(hours=0))

        direct_messages = [direct1, direct2]
        channel_messages = [channel1, channel2]

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.messages"].MessageDatabaseClient.get_direct_messages_previews.return_value = direct_messages
        sys.modules["daos.messages"].MessageDatabaseClient.get_channel_messages_previews.return_value = channel_messages

        response = MessageService.get_preview_messages(data)
        self.assertIsInstance(response, ChatsListResponse)
        self.assertEqual(4, len(response.chats))
        self.assertEqual(4, response.chats[0].get("chat_id"))
        self.assertEqual(False, response.chats[0].get("unseen"))
        self.assertEqual(5, response.chats[0].get("sender").get("id"))
        self.assertEqual(3, response.chats[1].get("chat_id"))
        self.assertEqual(False, response.chats[1].get("unseen"))
        self.assertEqual(0, response.chats[1].get("sender").get("id"))
        self.assertEqual(5, response.chats[2].get("chat_id"))
        self.assertEqual(False, response.chats[2].get("unseen"))
        self.assertEqual(5, response.chats[2].get("sender").get("id"))
        self.assertEqual(1, response.chats[3].get("chat_id"))
        self.assertEqual(True, response.chats[3].get("unseen"))
        self.assertEqual(0, response.chats[3].get("sender").get("id"))
        self.assertEqual(MessageResponseStatus.LIST.value, response.json().get("status"))
