import unittest
from unittest.mock import MagicMock

from dtos.models.users import PublicUser
from dtos.models.teams import Team
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
        data1 = MagicMock()
        data2 = MagicMock()

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

        NotificationService.notify_team_invitation(data1, data2)
        self.assertIsNone(MockedNotificationServer.notification)
