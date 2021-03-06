import unittest
from unittest.mock import MagicMock

from dtos.models.users import PublicUser
from dtos.models.teams import ForbiddenWord
from dtos.models.channels import Channel, ChannelCreator
from dtos.models.messages import *
from dtos.responses.messages import *
from models.constants import TeamRoles, MessageResponseStatus, SendMessageType, TeamResponseStatus
from exceptions.exceptions import ChatNotFoundError, WrongActionError
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

from services.messages import MessageService, WordCensor

mock = MagicMock()


class MockedMessageDatabase:
    stored_chat = None
    stored_chats = []
    stored_messages = []


class MessagesServiceTestCase(unittest.TestCase):

    def tearDown(self):
        MockedMessageDatabase.stored_chat = None
        MockedMessageDatabase.stored_chats = []
        MockedMessageDatabase.stored_messages = []

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

    def test_get_preview_messages_from_user_with_non_emtpy_chat_lists_work_properly(self):
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

    def test_get_messages_from_non_existent_chat_returns_not_found(self):
        data = MagicMock()

        '''Mocked ouputs'''
        user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.messages"].MessageDatabaseClient.get_chat_by_ids.return_value = None

        self.assertRaises(ChatNotFoundError, MessageService.get_messages_from_chat, data)

    def test_get_messages_from_direct_chat_set_offset_in_0_and_works_properly(self):
        data = MagicMock()

        '''Mocked ouputs'''
        user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value
        chat = Chat(user_id=0, chat_id=1, team_id=0, offset=1)
        sender1 = UserMessageSender(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        message1 = ChatMessage(message_id=1, sender=sender1, receiver_id=1, team_id=0, content="Test-Message-0",
                               message_type="TEXT", timestamp=datetime.now() - timedelta(hours=1))
        sender2 = UserMessageSender(user_id=1, username="Tester1", first_name="Test1", last_name="Test1")
        message2 = ChatMessage(message_id=0, sender=sender2, receiver_id=0, team_id=0, content="Test-Message-1",
                               message_type="TEXT", timestamp=datetime.now() - timedelta(hours=0))
        direct_chats = [message1, message2]

        def add_or_update_chat(chat):
            from tests.test_services import test_messages
            MockedMessageDatabase.stored_chat = chat

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.messages"].MessageDatabaseClient.get_chat_by_ids.return_value = chat
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = None
        sys.modules["daos.messages"].MessageDatabaseClient.get_direct_chat.return_value = direct_chats
        sys.modules["daos.messages"].MessageDatabaseClient.add_or_update_chat = MagicMock(
            side_effect=add_or_update_chat)

        response = MessageService.get_messages_from_chat(data)
        self.assertIsInstance(response, MessageListResponse)
        self.assertEqual(False, response.is_channel)
        self.assertEqual(2, len(response.messages))
        self.assertEqual(1, response.messages[0].get("sender").get("id"))
        self.assertEqual(0, response.messages[1].get("sender").get("id"))
        self.assertEqual(0, MockedMessageDatabase.stored_chat.offset)

    def test_get_messages_from_channel_chat_set_offset_in_0_and_works_properly(self):
        data = MagicMock()

        '''Mocked ouputs'''
        user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value
        chat = Chat(user_id=0, chat_id=1, team_id=0, offset=1)
        channel = Channel(channel_id=2, name="Channel-Test", creator=ChannelCreator(user_id=5), team_id=0)
        sender1 = UserMessageSender(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        message1 = ChatMessage(message_id=1, sender=sender1, receiver_id=2, team_id=0, content="Test-Message-0",
                               message_type="TEXT", timestamp=datetime.now() - timedelta(hours=1))
        sender2 = UserMessageSender(user_id=1, username="Tester1", first_name="Test1", last_name="Test1")
        message2 = ChatMessage(message_id=0, sender=sender2, receiver_id=2, team_id=0, content="Test-Message-1",
                               message_type="TEXT", timestamp=datetime.now() - timedelta(hours=0))
        channel_chats = [message1, message2]

        def add_update_chat(chat):
            from tests.test_services import test_messages
            MockedMessageDatabase.stored_chat = chat

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.messages"].MessageDatabaseClient.get_chat_by_ids.return_value = chat
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = channel
        sys.modules["daos.messages"].MessageDatabaseClient.get_channel_chat.return_value = channel_chats
        sys.modules["daos.messages"].MessageDatabaseClient.add_or_update_chat = MagicMock(side_effect=add_update_chat)

        response = MessageService.get_messages_from_chat(data)
        self.assertIsInstance(response, MessageListResponse)
        self.assertEqual(True, response.is_channel)
        self.assertEqual(2, len(response.messages))
        self.assertEqual(1, response.messages[0].get("sender").get("id"))
        self.assertEqual(0, response.messages[1].get("sender").get("id"))
        self.assertEqual(0, MockedMessageDatabase.stored_chat.offset)

    def test_send_message_to_yourself_returns_bad_request(self):
        data = MagicMock()
        data.chat_id = 0

        '''Mocked ouputs'''
        user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user

        self.assertRaises(WrongActionError, MessageService.send_message, data)

    def test_send_message_to_not_member_from_team_returns_bad_request(self):
        data = MagicMock()
        data.chat_id = 1

        '''Mocked ouputs'''
        user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value
        receiver = MessageReceiver(user_id=1, team_id=1, is_user=True)

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.messages"].MessageDatabaseClient.get_message_direct_receiver_by_ids.return_value = receiver

        response = MessageService.send_message(data)
        self.assertIsInstance(response, BadRequestMessageSentResponse)
        self.assertEqual(TeamResponseStatus.USER_NOT_MEMBER.value, response.status)

    def test_send_message_to_user_in_new_chat_works_properly(self):
        data = MagicMock()
        data.chat_id = 1

        '''Mocked ouputs'''
        user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value
        receiver = MessageReceiver(user_id=1, team_id=0, is_user=True)

        def add_update_chat(chat):
            from tests.test_services import test_messages
            MockedMessageDatabase.stored_chats += [chat]

        def add_message(message):
            from tests.test_services import test_messages
            message.message_id = 0
            MockedMessageDatabase.stored_messages += [message]
            return message

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.messages"].MessageDatabaseClient.get_message_direct_receiver_by_ids.return_value = receiver
        sys.modules["daos.messages"].MessageDatabaseClient.get_chat_by_ids.return_value = None
        sys.modules["daos.messages"].MessageDatabaseClient.add_message = MagicMock(side_effect=add_message)
        sys.modules["daos.messages"].MessageDatabaseClient.add_or_update_chat = MagicMock(side_effect=add_update_chat)

        response = MessageService.send_message(data)

        self.assertIsInstance(response, SuccessfulMessageSentResponse)
        self.assertEqual(1, len(MockedMessageDatabase.stored_messages))
        self.assertEqual(2, len(MockedMessageDatabase.stored_chats))
        self.assertEqual(0, MockedMessageDatabase.stored_messages[0].message_id)
        self.assertEqual(MessageResponseStatus.SENT.value, response.json().get("status"))

    def test_send_message_to_channel_in_new_chat_works_properly(self):
        data = MagicMock()
        data.chat_id = 1

        '''Mocked ouputs'''
        user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        user.team_id = 0
        user.team_role = TeamRoles.MEMBER.value
        receiver = MessageReceiver(user_id=None, team_id=0, is_user=False)
        member1 = PublicUser(user_id=1, username="Tester1", email="test1@test", first_name="Test1", last_name="Test1",
                             profile_pic=None, role="MEMBER", online=False)
        member2 = PublicUser(user_id=2, username="Tester2", email="test2@test", first_name="Test2", last_name="Test2",
                             profile_pic=None, role="MEMBER", online=False)
        members = [member1, member2]

        def add_update_chat(chat):
            from tests.test_services import test_messages
            MockedMessageDatabase.stored_chats += [chat]

        def add_message(message):
            from tests.test_services import test_messages
            message.message_id = 0
            MockedMessageDatabase.stored_messages += [message]
            return message

        sys.modules["models.authentication"].Authenticator.authenticate_team.return_value = user
        sys.modules["daos.messages"].MessageDatabaseClient.get_message_direct_receiver_by_ids.return_value = None
        sys.modules["daos.messages"].MessageDatabaseClient.get_message_channel_receiver_by_ids.return_value = receiver
        sys.modules["daos.messages"].MessageDatabaseClient.get_chat_by_ids.return_value = None
        sys.modules["daos.messages"].MessageDatabaseClient.add_message = MagicMock(side_effect=add_message)
        sys.modules["daos.messages"].MessageDatabaseClient.add_or_update_chat = MagicMock(side_effect=add_update_chat)
        sys.modules["daos.channels"].ChannelDatabaseClient.get_all_channel_users_by_channel_id.return_value = members

        response = MessageService.send_message(data)

        self.assertIsInstance(response, SuccessfulMessageSentResponse)
        self.assertEqual(1, len(MockedMessageDatabase.stored_messages))
        self.assertEqual(3, len(MockedMessageDatabase.stored_chats))
        self.assertEqual(0, MockedMessageDatabase.stored_messages[0].message_id)
        self.assertEqual(MessageResponseStatus.SENT.value, response.json().get("status"))

    def test_censor_forbidden_word_works_properly(self):
        message = MagicMock()
        message.content = "This is a test!"
        message.message_type = MessageType.TEXT.value

        '''Mocked ouputs'''
        forbidden_words = [ForbiddenWord(word_id=0, word="test", team_id=0)]
        sys.modules["daos.teams"].TeamDatabaseClient.get_forbidden_words_from_team.return_value = forbidden_words
        self.assertEqual("This is a ****!", WordCensor(0).remove_forbidden_words(message))
