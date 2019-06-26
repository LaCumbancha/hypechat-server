import unittest
from unittest.mock import MagicMock

from dtos.models.bots import Bot
from dtos.models.users import PublicUser
from dtos.models.teams import Team, TeamUser
from dtos.models.channels import Channel, ChannelCreator, ChannelUser
from dtos.models.messages import Message
from models.constants import TeamRoles, NotificationType, SendMessageType, MessageType

'''Mocking environment properties'''
import sys
sys.modules["daos.bots"] = MagicMock()
sys.modules["daos.users"] = MagicMock()
sys.modules["daos.channels"] = MagicMock()
sys.modules["daos.teams"] = MagicMock()
sys.modules["pyfcm"] = MagicMock()
sys.modules["logging"].getLogger = MagicMock()
sys.modules["os"].getenv = MagicMock(side_effect=lambda key: environment_properties.get(key))

environment_properties = {
    'FIREBASE_API_KEY': "TEST"
}

from services.notifications import NotificationService

mock = MagicMock()


class MockedNotificationServer:
    notification = None


class Notification:

    def __init__(self, topic_name, message_title, message_body, data_message):
        self.topic_name = topic_name
        self.message_title = message_title
        self.message_body = message_body
        self.data_message = data_message


class NotificationServiceTestCase(unittest.TestCase):

    def tearDown(self):
        MockedNotificationServer.notification = None

    def test_notify_team_invitation_to_non_registered_user_does_not_send_notification(self):
        invitation = MagicMock()
        inviter_id = MagicMock()

        '''Mocked outputs'''
        inviter_user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = inviter_user
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_team_invitation(invitation, inviter_id)
        self.assertIsNone(MockedNotificationServer.notification)

    def test_notify_team_invitation_to_registered_user_does_send_notification(self):
        invitation = MagicMock()
        inviter_id = MagicMock()

        '''Mocked outputs'''
        inviter_user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        invited_user = PublicUser(user_id=1, username="Tester1", first_name="Test1", last_name="Test1")
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = inviter_user
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_email.return_value = invited_user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_team_invitation(invitation, inviter_id)
        self.assertEqual(1, MockedNotificationServer.notification.topic_name)
        self.assertEqual("Hypechat", MockedNotificationServer.notification.message_title)
        self.assertEqual("You have been invited to join a team!", MockedNotificationServer.notification.message_body)
        self.assertEqual("Test-Team", MockedNotificationServer.notification.data_message.get("team_name"))
        self.assertEqual(0, MockedNotificationServer.notification.data_message.get("inviter").get("id"))
        self.assertEqual("Tester0", MockedNotificationServer.notification.data_message.get("inviter").get("username"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("inviter").get("first_name"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("inviter").get("last_name"))
        self.assertEqual(NotificationType.TEAM_INVITATION.value,
                         MockedNotificationServer.notification.data_message.get("notification_type"))

    def test_notify_team_role_change_sends_notification(self):
        user_team = TeamUser(user_id=1, team_id=0, role=TeamRoles.MODERATOR.value)
        admin_id = 0

        '''Mocked outputs'''
        admin = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        old_role = TeamRoles.MEMBER.value
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = admin
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_change_role(user_team, old_role, admin_id)
        self.assertEqual(1, MockedNotificationServer.notification.topic_name)
        self.assertEqual("Hypechat", MockedNotificationServer.notification.message_title)
        self.assertEqual("You have been upgraded in team Test-Team!", MockedNotificationServer.notification.message_body)
        self.assertEqual("Test-Team", MockedNotificationServer.notification.data_message.get("team_name"))
        self.assertEqual(0, MockedNotificationServer.notification.data_message.get("admin").get("id"))
        self.assertEqual("Tester0", MockedNotificationServer.notification.data_message.get("admin").get("username"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("admin").get("first_name"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("admin").get("last_name"))
        self.assertEqual(NotificationType.TEAM_ROLE_CHANGE.value,
                         MockedNotificationServer.notification.data_message.get("notification_type"))

    def test_notify_channel_invitation_sends_notification(self):
        user_channel = ChannelUser(user_id=1, channel_id=0)
        inviter_id = 0

        '''Mocked outputs'''
        inviter_user = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        channel = Channel(channel_id=0, team_id=0, name="Test-Channel",
                          creator=ChannelCreator(0, "Tester0", "Test0", "Test0"))
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = inviter_user
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = channel
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_channel_invitation(user_channel, inviter_id)
        self.assertEqual(1, MockedNotificationServer.notification.topic_name)
        self.assertEqual("Hypechat", MockedNotificationServer.notification.message_title)
        self.assertEqual("You have been added to channel Test-Channel in team Test-Team!",
                         MockedNotificationServer.notification.message_body)
        self.assertEqual("Test-Team", MockedNotificationServer.notification.data_message.get("team_name"))
        self.assertEqual("Test-Channel", MockedNotificationServer.notification.data_message.get("channel_name"))
        self.assertEqual(0, MockedNotificationServer.notification.data_message.get("inviter").get("id"))
        self.assertEqual("Tester0", MockedNotificationServer.notification.data_message.get("inviter").get("username"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("inviter").get("first_name"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("inviter").get("last_name"))
        self.assertEqual(NotificationType.CHANNEL_INVITATION.value,
                         MockedNotificationServer.notification.data_message.get("notification_type"))

    def test_notify_direct_message_from_user_sends_notification(self):
        message = Message(sender_id=0, receiver_id=1, team_id=0, content="Sarasa",
                          send_type=SendMessageType.DIRECT.value, message_type=MessageType.TEXT.value)
        is_user_receiver = True

        '''Mocked outputs'''
        user_sender = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user_sender
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = None
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_message(message, is_user_receiver)
        self.assertEqual(1, MockedNotificationServer.notification.topic_name)
        self.assertEqual("Hypechat", MockedNotificationServer.notification.message_title)
        self.assertEqual("You receive a direct message!", MockedNotificationServer.notification.message_body)
        self.assertEqual("Test-Team", MockedNotificationServer.notification.data_message.get("team_name"))
        self.assertEqual(0, MockedNotificationServer.notification.data_message.get("sender").get("id"))
        self.assertEqual("Tester0", MockedNotificationServer.notification.data_message.get("sender").get("username"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("sender").get("first_name"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("sender").get("last_name"))
        self.assertEqual(NotificationType.MESSAGE.value,
                         MockedNotificationServer.notification.data_message.get("notification_type"))

    def test_notify_direct_message_from_bot_sends_notification(self):
        message = Message(sender_id=0, receiver_id=1, team_id=0, content="Sarasa",
                          send_type=SendMessageType.DIRECT.value, message_type=MessageType.TEXT.value)
        is_user_receiver = True

        '''Mocked outputs'''
        bot_sender = Bot(bot_id=0, name="Test-Bot", callback=None, token=None)
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = None
        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = bot_sender
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = None
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_message(message, is_user_receiver)
        self.assertEqual(1, MockedNotificationServer.notification.topic_name)
        self.assertEqual("Hypechat", MockedNotificationServer.notification.message_title)
        self.assertEqual("You receive a direct message!", MockedNotificationServer.notification.message_body)
        self.assertEqual("Test-Team", MockedNotificationServer.notification.data_message.get("team_name"))
        self.assertEqual(0, MockedNotificationServer.notification.data_message.get("sender").get("id"))
        self.assertEqual("Test-Bot", MockedNotificationServer.notification.data_message.get("sender").get("name"))
        self.assertEqual(NotificationType.MESSAGE.value,
                         MockedNotificationServer.notification.data_message.get("notification_type"))

    def test_notify_channel_message_from_user_sends_notification(self):
        message = Message(sender_id=0, receiver_id=1, team_id=0, content="Sarasa",
                          send_type=SendMessageType.DIRECT.value, message_type=MessageType.TEXT.value)
        is_user_receiver = False

        '''Mocked outputs'''
        user_sender = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        channel = Channel(channel_id=0, team_id=0, name="Test-Channel",
                          creator=ChannelCreator(0, "Tester0", "Test0", "Test0"))
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user_sender
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = channel
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_message(message, is_user_receiver)
        self.assertEqual(1, MockedNotificationServer.notification.topic_name)
        self.assertEqual("Hypechat", MockedNotificationServer.notification.message_title)
        self.assertEqual("You receive a channel message!", MockedNotificationServer.notification.message_body)
        self.assertEqual("Test-Team", MockedNotificationServer.notification.data_message.get("team_name"))
        self.assertEqual("Test-Channel", MockedNotificationServer.notification.data_message.get("channel_name"))
        self.assertEqual(0, MockedNotificationServer.notification.data_message.get("sender").get("id"))
        self.assertEqual("Tester0", MockedNotificationServer.notification.data_message.get("sender").get("username"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("sender").get("first_name"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("sender").get("last_name"))
        self.assertEqual(NotificationType.MESSAGE.value,
                         MockedNotificationServer.notification.data_message.get("notification_type"))

    def test_notify_channel_message_from_bot_sends_notification(self):
        message = Message(sender_id=0, receiver_id=1, team_id=0, content="Sarasa",
                          send_type=SendMessageType.DIRECT.value, message_type=MessageType.TEXT.value)
        is_user_receiver = False

        '''Mocked outputs'''
        bot_sender = Bot(bot_id=0, name="Test-Bot", callback=None, token=None)
        channel = Channel(channel_id=0, team_id=0, name="Test-Channel",
                          creator=ChannelCreator(0, "Tester0", "Test0", "Test0"))
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = None
        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = bot_sender
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = channel
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_message(message, is_user_receiver)
        self.assertEqual(1, MockedNotificationServer.notification.topic_name)
        self.assertEqual("Hypechat", MockedNotificationServer.notification.message_title)
        self.assertEqual("You receive a channel message!", MockedNotificationServer.notification.message_body)
        self.assertEqual("Test-Team", MockedNotificationServer.notification.data_message.get("team_name"))
        self.assertEqual("Test-Channel", MockedNotificationServer.notification.data_message.get("channel_name"))
        self.assertEqual(0, MockedNotificationServer.notification.data_message.get("sender").get("id"))
        self.assertEqual("Test-Bot", MockedNotificationServer.notification.data_message.get("sender").get("name"))
        self.assertEqual(NotificationType.MESSAGE.value,
                         MockedNotificationServer.notification.data_message.get("notification_type"))

    def test_notify_mention_to_bot_does_not_send_notification(self):
        message = Message(sender_id=0, receiver_id=1, team_id=0, content="Sarasa",
                          send_type=SendMessageType.DIRECT.value, message_type=MessageType.TEXT.value)
        mentioned_id = 1

        '''Mocked outputs'''
        bot_mentioned = Bot(bot_id=0, name="Test-Bot", callback=None, token=None)

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = bot_mentioned
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_mention(message, mentioned_id)
        self.assertIsNone(MockedNotificationServer.notification)

    def test_notify_mention_to_user_from_user_in_channel_does_send_notification(self):
        message = Message(sender_id=0, receiver_id=1, team_id=0, content="Sarasa",
                          send_type=SendMessageType.DIRECT.value, message_type=MessageType.TEXT.value)
        mentioned_id = 1

        '''Mocked outputs'''
        user_sender = PublicUser(user_id=0, username="Tester0", first_name="Test0", last_name="Test0")
        channel = Channel(channel_id=0, team_id=0, name="Test-Channel",
                          creator=ChannelCreator(0, "Tester0", "Test0", "Test0"))
        team = Team(team_id=0, name="Test-Team")

        def send_notification(topic_name, message_title, message_body, data_message):
            from tests.test_services import test_notifications
            MockedNotificationServer.notification = Notification(topic_name, message_title, message_body, data_message)
            return {"failure": 0}

        sys.modules["daos.bots"].BotDatabaseClient.get_bot_by_id.return_value = None
        sys.modules["daos.teams"].TeamDatabaseClient.get_team_by_id.return_value = team
        sys.modules["daos.users"].UserDatabaseClient.get_user_by_id.return_value = user_sender
        sys.modules["daos.channels"].ChannelDatabaseClient.get_channel_by_id.return_value = channel
        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_mention(message, mentioned_id)
        self.assertEqual(1, MockedNotificationServer.notification.topic_name)
        self.assertEqual("Hypechat", MockedNotificationServer.notification.message_title)
        self.assertEqual("You have been mentioned!", MockedNotificationServer.notification.message_body)
        self.assertEqual("Test-Team", MockedNotificationServer.notification.data_message.get("team_name"))
        self.assertEqual("Test-Channel", MockedNotificationServer.notification.data_message.get("channel_name"))
        self.assertEqual(0, MockedNotificationServer.notification.data_message.get("sender").get("id"))
        self.assertEqual("Tester0", MockedNotificationServer.notification.data_message.get("sender").get("username"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("sender").get("first_name"))
        self.assertEqual("Test0", MockedNotificationServer.notification.data_message.get("sender").get("last_name"))
        self.assertEqual(NotificationType.MENTION.value,
                         MockedNotificationServer.notification.data_message.get("notification_type"))

    def test_when_connection_error_is_raised_by_pyfcm_notification_is_not_send(self):

        def send_notification(topic_name, message_title, message_body, data_message):
            raise ConnectionError

        sys.modules["pyfcm"].FCMNotification().notify_topic_subscribers = MagicMock(side_effect=send_notification)

        NotificationService.notify_team_invitation(mock, mock)
        self.assertIsNone(MockedNotificationServer.notification)
        NotificationService.notify_channel_invitation(mock, mock)
        self.assertIsNone(MockedNotificationServer.notification)
        NotificationService.notify_message(mock, mock)
        self.assertIsNone(MockedNotificationServer.notification)
        NotificationService.notify_mention(mock, mock)
        self.assertIsNone(MockedNotificationServer.notification)
