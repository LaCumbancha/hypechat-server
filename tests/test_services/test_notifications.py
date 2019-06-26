import unittest
from unittest.mock import MagicMock

from dtos.models.users import PublicUser
from dtos.models.teams import Team, TeamUser
from models.constants import TeamRoles, NotificationType

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
        pass

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
