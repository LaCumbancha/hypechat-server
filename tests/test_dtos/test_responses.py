import unittest
from unittest.mock import MagicMock

from dtos.responses.channels import *
from dtos.responses.clients import *
from dtos.responses.messages import *
from dtos.responses.teams import *

import sys
sys.modules["logging"].getLogger = MagicMock()

from models.constants import UserResponseStatus


class ResponseTestCase(unittest.TestCase):

    def test_successful_user_response_returns_status_code_200(self):
        user = MagicMock()
        response = SuccessfulUserResponse(user)
        self.assertEqual(response.status_code(), 200)

    def test_successful_user_response_returns_json_body_with_user_key(self):
        user = MagicMock()
        response = SuccessfulUserResponse(user)
        self.assertTrue("user" in response.json())

    def test_successful_user_response_returns_active_status_depending_on_online_attribute(self):
        user1 = MagicMock()
        user2 = MagicMock()
        user1.online = True
        user2.online = False
        response1 = SuccessfulUserResponse(user1)
        response2 = SuccessfulUserResponse(user2)
        self.assertEqual(response1.json().get("status"), UserResponseStatus.ACTIVE.value,
                         msg="Response status should be ACTIVE but it's OFFLINE.")
        self.assertEqual(response2.json().get("status"), UserResponseStatus.OFFLINE.value,
                         msg="Response status should be OFFLINE but it's ACTIVE.")

    def test_successful_full_user_response_returns_status_code_200(self):
        user = MagicMock()
        response = SuccessfulFullUserResponse(user)
        self.assertEqual(response.status_code(), 200)

    def test_successful_full_user_response_returns_active_status_always(self):
        user1 = MagicMock()
        user2 = MagicMock()
        user1.online = True
        user2.online = False
        response1 = SuccessfulFullUserResponse(user1)
        response2 = SuccessfulFullUserResponse(user2)
        self.assertEqual(response1.json().get("status"), UserResponseStatus.ACTIVE.value,
                         msg="Response status should be ACTIVE but it's OFFLINE.")
        self.assertEqual(response2.json().get("status"), UserResponseStatus.ACTIVE.value,
                         msg="Response status should be ACTIVE but it's OFFLINE.")

    def test_successful_users_list_response_returns_status_code_200_with_status_list(self):
        users = MagicMock()
        response = SuccessfulUsersListResponse(users)
        self.assertEqual(response.status_code(), 200)
        self.assertEqual(response.json().get("status"), UserResponseStatus.LIST.value)

    def test_unsuccessful_user_message_response_returns_status_code_500_with_status_error(self):
        message = MagicMock()
        response = UnsuccessfulClientResponse(message)
        self.assertEqual(response.status_code(), 500)
        self.assertEqual(response.json().get("status"), UserResponseStatus.ERROR.value)

    def test_bad_request_user_message_response_returns_status_code_400_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response1 = BadRequestUserMessageResponse(message, status1)
        response2 = BadRequestUserMessageResponse(message, status2)
        self.assertEqual(response1.status_code(), 400)
        self.assertEqual(response2.status_code(), 400)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_not_found_user_message_response_returns_status_code_404_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response2 = NotFoundUserMessageResponse(message, status2)
        response1 = NotFoundUserMessageResponse(message, status1)
        self.assertEqual(response1.status_code(), 404)
        self.assertEqual(response2.status_code(), 404)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_successful_user_message_response_returns_status_code_200_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response2 = SuccessfulUserMessageResponse(message, status2)
        response1 = SuccessfulUserMessageResponse(message, status1)
        self.assertEqual(response1.status_code(), 200)
        self.assertEqual(response2.status_code(), 200)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_successful_team_response_returns_json_body_with_team_key_with_custom_status(self):
        team = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response1 = SuccessfulTeamResponse(team, status1)
        response2 = SuccessfulTeamResponse(team, status2)
        self.assertTrue("team" in response1.json())
        self.assertTrue("team" in response2.json())
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_successful_team_response_returns_status_code_200_with_custom_status(self):
        team = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response2 = SuccessfulTeamResponse(team, status2)
        response1 = SuccessfulTeamResponse(team, status1)
        self.assertEqual(response1.status_code(), 200)
        self.assertEqual(response2.status_code(), 200)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_successful_teams_list_response_returns_status_code_200_with_status_list(self):
        teams = MagicMock()
        response = SuccessfulTeamsListResponse(teams)
        self.assertEqual(response.status_code(), 200)
        self.assertEqual(response.json().get("status"), TeamResponseStatus.LIST.value)

    def test_successful_forbidden_words_list_response_returns_status_code_200_with_status_list(self):
        words = MagicMock()
        response = SuccessfulForbiddenWordsList(words)
        self.assertEqual(response.status_code(), 200)
        self.assertEqual(response.json().get("status"), TeamResponseStatus.LIST.value)

    def test_successful_team_message_response_returns_status_code_200_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response2 = SuccessfulTeamMessageResponse(message, status2)
        response1 = SuccessfulTeamMessageResponse(message, status1)
        self.assertEqual(response1.status_code(), 200)
        self.assertEqual(response2.status_code(), 200)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_bad_request_team_message_response_returns_status_code_400_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response1 = BadRequestTeamMessageResponse(message, status1)
        response2 = BadRequestTeamMessageResponse(message, status2)
        self.assertEqual(response1.status_code(), 400)
        self.assertEqual(response2.status_code(), 400)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_forbidden_team_message_response_returns_status_code_403_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response1 = ForbiddenTeamMessageResponse(message, status1)
        response2 = ForbiddenTeamMessageResponse(message, status2)
        self.assertEqual(response1.status_code(), 403)
        self.assertEqual(response2.status_code(), 403)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_not_found_team_message_response_returns_status_code_404_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response2 = NotFoundTeamMessageResponse(message, status2)
        response1 = NotFoundTeamMessageResponse(message, status1)
        self.assertEqual(response1.status_code(), 404)
        self.assertEqual(response2.status_code(), 404)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_unsuccessful_team_message_response_returns_status_code_500_with_status_error(self):
        message = MagicMock()
        response = UnsuccessfulTeamMessageResponse(message)
        self.assertEqual(response.status_code(), 500)
        self.assertEqual(response.json().get("status"), UserResponseStatus.ERROR.value)

    def test_successful_channel_response_returns_json_body_with_channel_key_with_custom_status(self):
        channel = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response1 = SuccessfulChannelResponse(channel, status1)
        response2 = SuccessfulChannelResponse(channel, status2)
        self.assertTrue("channel" in response1.json())
        self.assertTrue("channel" in response2.json())
        self.assertEqual(response1.json()["status"], status1)
        self.assertEqual(response2.json()["status"], status2)

    def test_successful_channels_list_response_returns_status_code_200_with_status_list(self):
        channels = MagicMock()
        response = SuccessfulChannelsListResponse(channels)
        self.assertEqual(response.status_code(), 200)
        self.assertEqual(response.json().get("status"), TeamResponseStatus.LIST.value)

    def test_successful_channel_message_response_returns_status_code_200_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response2 = SuccessfulChannelMessageResponse(message, status2)
        response1 = SuccessfulChannelMessageResponse(message, status1)
        self.assertEqual(response1.status_code(), 200)
        self.assertEqual(response2.status_code(), 200)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_bad_request_channel_message_response_returns_status_code_400_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response1 = BadRequestChannelMessageResponse(message, status1)
        response2 = BadRequestChannelMessageResponse(message, status2)
        self.assertEqual(response1.status_code(), 400)
        self.assertEqual(response2.status_code(), 400)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_forbidden_channel_message_response_returns_status_code_403_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response1 = ForbiddenChannelMessageResponse(message, status1)
        response2 = ForbiddenChannelMessageResponse(message, status2)
        self.assertEqual(response1.status_code(), 403)
        self.assertEqual(response2.status_code(), 403)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_not_found_channel_message_response_returns_status_code_404_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response2 = NotFoundChannelMessageResponse(message, status2)
        response1 = NotFoundChannelMessageResponse(message, status1)
        self.assertEqual(response1.status_code(), 404)
        self.assertEqual(response2.status_code(), 404)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)

    def test_unsuccessful_channel_message_response_returns_status_code_500_with_status_error(self):
        message = MagicMock()
        response = UnsuccessfulChannelMessageResponse(message)
        self.assertEqual(response.status_code(), 500)
        self.assertEqual(response.json().get("status"), UserResponseStatus.ERROR.value)

    def test_successful_message_sent_response_returns_status_code_200(self):
        message = MagicMock()
        response = SuccessfulMessageSentResponse(message)
        self.assertEqual(response.status_code(), 200)

    def test_successful_message_response_returns_json_body_with_user_key(self):
        message = MagicMock()
        response = SuccessfulMessageSentResponse(message)
        self.assertTrue("message" in response.json())

    def test_unsuccessful_message_sent_response_returns_status_code_500_with_status_error(self):
        message = MagicMock()
        response = UnsuccessfulMessageSentResponse(message)
        self.assertEqual(response.status_code(), 500)
        self.assertEqual(response.json().get("status"), UserResponseStatus.ERROR.value)

    def test_messages_list_response_returns_status_code_200_with_status_list_and_key_messages(self):
        messages = MagicMock()
        response = MessageListResponse(messages)
        self.assertTrue("messages" in response.json())
        self.assertEqual(response.status_code(), 200)
        self.assertEqual(response.json().get("status"), MessageResponseStatus.LIST.value)

    def test_chats_list_response_returns_status_code_200_with_status_list_and_key_messages(self):
        chats = MagicMock()
        response = ChatsListResponse(chats)
        self.assertTrue("chats" in response.json())
        self.assertEqual(response.status_code(), 200)
        self.assertEqual(response.json().get("status"), MessageResponseStatus.LIST.value)

    def test_bad_request_message_sent_response_returns_status_code_400_with_custom_status(self):
        message = MagicMock()
        status1 = "TEST1"
        status2 = "TEST2"
        response1 = BadRequestMessageSentResponse(message, status1)
        response2 = BadRequestMessageSentResponse(message, status2)
        self.assertEqual(response1.status_code(), 400)
        self.assertEqual(response2.status_code(), 400)
        self.assertEqual(response1.json().get("status"), status1)
        self.assertEqual(response2.json().get("status"), status2)
