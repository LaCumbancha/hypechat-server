import unittest
from unittest.mock import MagicMock

from dtos.inputs.users import *
from dtos.inputs.teams import *
from dtos.inputs.channels import *
from dtos.inputs.messages import *
from models.request import ClientRequest
from exceptions.exceptions import *

import sys
sys.modules["logging"].getLogger = MagicMock()

mock = None
EMPTY_DICTIONARY = {}
authentication_headers = {"X-Auth-Token": "test"}


class Header:

    def __init__(self, headers):
        self.headers = headers

    def to_list(self):
        return self.headers.items()

    def get(self, key):
        return self.headers.get(key)


class Request:

    def __init__(self, body=None, headers=None, args=None):
        self.body = body
        self.is_json = body is not None
        self.args = {} if args is None else args
        self.headers = Header(EMPTY_DICTIONARY if headers is None else headers)

    def get_json(self):
        return self.body

    def headers(self):
        return self.headers


class ClientRequestTestCase(unittest.TestCase):

    def test_new_user_data_without_email_throws_exception(self):
        body_json = {"username": "test", "password": "pass"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_without_username_throws_exception(self):
        body_json = {"password": "pass", "email": "test@test"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_without_password_throws_exception(self):
        body_json = {"username": "test", "email": "test@test"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_with_full_data_works_properly(self):
        body_json = {"username": "test", "password": "pass", "email": "test@test"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.new_user_data(), NewUserDTO)

    def test_app_login_data_without_password_throws_exception(self):
        body_json = {"email": "test@test"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.login_data)

    def test_app_login_data_without_email_throws_exception(self):
        body_json = {"password": "pass"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.login_data)

    def test_login_data_with_full_data_works_properly(self):
        body_json_app = {"email": "test@test", "password": "pass"}
        body_json_face = {"facebook_token": "token-test"}
        input_request_app = Request(body=body_json_app)
        input_request_face = Request(body=body_json_face)
        client_request_app = ClientRequest(input_request_app)
        client_request_face = ClientRequest(input_request_face)
        self.assertIsInstance(client_request_app.login_data(), LoginDTO)
        self.assertIsInstance(client_request_face.login_data(), LoginDTO)

    def test_recover_password_data_without_email_throws_exception(self):
        recover_json = {}
        input_request = Request(body=recover_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.recover_password_data)

    def test_recover_password_data_with_full_data_works_properly(self):
        recover_json = {"email": "test@test"}
        input_request = Request(body=recover_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.recover_password_data(), RecoverPasswordDTO)

    def test_regenerate_password_data_without_email_throws_exception(self):
        body_json = {"recover_token": "test"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.regenerate_password_data)

    def test_regenerate_password_data_without_recovery_token_throws_exception(self):
        body_json = {"recover_token": "test"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.regenerate_password_data)

    def test_regenerate_password_data_with_full_data_works_properly(self):
        body_json = {"recover_token": "test", "email": "test@test"}
        input_request = Request(body=body_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.regenerate_password_data(), RegeneratePasswordDTO)

    def test_user_update_with_authentication_header_works_properly(self):
        body_json = {}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.user_update_data(), UserUpdateDTO)

    def test_search_users_by_username_with_authentication_header_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.search_users_by_username_data(mock, mock), SearchUsersDTO)

    def test_search_user_by_id_with_authentication_header_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.team_user_profile_data(mock, mock), SearchUserByIdDTO)

    def test_authentication_data_with_authentication_header_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.authentication_data(), AuthenticationDTO)

    def test_inbox_data_without_team_id_throws_exception(self):
        body_json = {"chat_id": 0, "content": "test", "message_type": "UNKNOWN"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.inbox_data)

    def test_inbox_data_without_chat_id_throws_exception(self):
        body_json = {"team_id": 0, "content": "test", "message_type": "UNKNOWN"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.inbox_data)

    def test_inbox_data_without_content_throws_exception(self):
        body_json = {"team_id": 0, "chat_id": 0, "message_type": "UNKNOWN"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.inbox_data)

    def test_inbox_data_without_message_type_throws_exception(self):
        body_json = {"team_id": 0, "chat_id": 0, "content": "test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.inbox_data)

    def test_inbox_data_with_unknown_message_type_throws_exception(self):
        body_json = {"team_id": 0, "chat_id": 0, "content": "test", "message_type": "UNKNOWN"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MessageTypeNotAvailableError, client_request.inbox_data)

    def test_inbox_data_with_full_data_works_properly(self):
        body_json = {"team_id": 0, "chat_id": 0, "content": "test", "message_type": "TEXT"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.inbox_data(), InboxDTO)

    def test_chat_data_with_full_data_and_no_offset_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.chat_data(mock, mock), ChatDTO)

    def test_chat_data_with_full_data_and_offset_works_properly(self):
        args = {"offset": 0}
        input_request = Request(headers=authentication_headers, args=args)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.chat_data(mock, mock), ChatDTO)

    def test_new_team_data_without_team_name_throws_exception(self):
        body_json = {}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_team_data)

    def test_new_team_data_with_full_data_works_properly(self):
        body_json = {"team_name": "test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.new_team_data(), NewTeamDTO)

    def test_add_user_to_team_data_without_team_id_throws_exception(self):
        body_json = {"add_user_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_team_data)

    def test_add_user_to_team_data_without_add_user_id_throws_exception(self):
        body_json = {"team_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_team_data)

    def test_add_user_to_team_data_with_full_data_works_properly(self):
        body_json = {"team_id": 0, "add_user_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.add_user_team_data(), AddUserTeamDTO)

    def test_invite_user_to_team_data_without_team_id_throws_exception(self):
        body_json = {"email": "test@test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.team_invite_data)

    def test_invite_user_to_team_data_without_email_throws_exception(self):
        body_json = {"team_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.team_invite_data)

    def test_invite_user_to_team_data_with_full_data_works_properly(self):
        body_json = {"team_id": 0, "email": "test@test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.team_invite_data(), TeamInviteDTO)

    def test_accept_invite_data_without_invite_token_throws_exception(self):
        body_json = {}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.accept_team_invite_data)

    def test_accept_invite_data_with_full_data_works_properly(self):
        body_json = {"invite_token": "test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.accept_team_invite_data(), TeamInviteAcceptDTO)

    def test_change_role_data_without_user_id_throws_exception(self):
        body_json = {"new_role": "UNKNOWN"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.change_role_data, mock)

    def test_change_role_data_without_new_role_throws_exception(self):
        body_json = {"user_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.change_role_data, mock)

    def test_change_role_data_with_unknown_new_role_throws_exception(self):
        body_json = {"user_id": 0, "new_role": "UNKNOWN"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(RoleNotAvailableError, client_request.change_role_data, mock)

    def test_change_role_data_with_full_data_works_properly(self):
        body_json = {"user_id": 0, "new_role": "MODERATOR"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.change_role_data(mock), ChangeRoleDTO)

    def test_team_authentication_data_with_authentication_header_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.team_authentication_data(mock), TeamAuthenticationDTO)

    def test_delete_user_team_data_with_authentication_header_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.delete_user_team_data(mock, mock), DeleteUserTeamDTO)

    def test_update_team_data_with_authentication_header_works_properly(self):
        body_json = {}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.team_update_data(mock), TeamUpdateDTO)

    def test_new_channel_data_without_team_id_throws_exception(self):
        body_json = {"name": "test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_channel_data)

    def test_new_channel_data_without_channel_name_throws_exception(self):
        body_json = {"team_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_channel_data)

    def test_new_channel_data_with_unknown_visibility_throws_exception(self):
        body_json = {"team_id": 0, "name": "test", "visibility": "UNKNOWN"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(VisibilityNotAvailableError, client_request.new_channel_data)

    def test_new_channel_data_with_full_data_with_visibility_works_properly(self):
        body_json = {"team_id": 0, "name": "test", "visibility": "PUBLIC"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.new_channel_data(), NewChannelDTO)

    def test_new_channel_data_with_full_data_without_visibility_works_properly(self):
        body_json = {"team_id": 0, "name": "test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.new_channel_data(), NewChannelDTO)

    def test_channel_invitation_data_without_team_id_throws_exception(self):
        body_json = {"channel_id": 0, "user_invited_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.channel_invitation_data)

    def test_channel_invitation_data_without_channel_id_throws_exception(self):
        body_json = {"team_id": 0, "user_invited_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.channel_invitation_data)

    def test_channel_invitation_data_without_user_invited_id_throws_exception(self):
        body_json = {"team_id": 0, "channel_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.channel_invitation_data)

    def test_channel_invitation_data_with_full_data_works_properly(self):
        body_json = {"team_id": 0, "channel_id": 0, "user_invited_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.channel_invitation_data(), ChannelInvitationDTO)

    def test_channel_registration_data_without_team_id_throws_exception(self):
        body_json = {"channel_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.channel_registration_data)

    def test_channel_registration_data_without_channel_id_throws_exception(self):
        body_json = {"team_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.channel_registration_data)

    def test_channel_registration_data_with_full_data_works_properly(self):
        body_json = {"team_id": 0, "channel_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.channel_registration_data(), ChannelRegistrationDTO)

    def test_delete_user_channel_data_with_authentication_header_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.delete_user_channel_data(mock, mock, mock), DeleteUserChannelDTO)

    def test_channel_authentication_data_with_authentication_header_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.channel_authentication_data(mock, mock), ChannelAuthenticationDTO)

    def test_update_channel_data_with_authentication_header_works_properly(self):
        body_json = {}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.channel_update_data(mock, mock), ChannelUpdateDTO)

    def test_add_forbidden_word_data_without_team_id_throws_exception(self):
        body_json = {"word": "test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.add_forbidden_word_data)

    def test_add_forbidden_word_data_without_word_throws_exception(self):
        body_json = {"team_id": 0}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.add_forbidden_word_data)

    def test_add_forbidden_word_data_with_full_data_works_properly(self):
        body_json = {"team_id": 0, "word": "test"}
        input_request = Request(body=body_json, headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.add_forbidden_word_data(), AddForbiddenWordDTO)

    def test_delete_forbidden_word_data_with_authentication_header_works_properly(self):
        input_request = Request(headers=authentication_headers)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.delete_forbidden_word_data(mock, mock), DeleteForbiddenWordDTO)

    def test_secure_actions_without_authentication_token_throws_exception(self):
        input_request = Request(EMPTY_DICTIONARY)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestHeaderError, client_request.user_update_data)
        self.assertRaises(MissingRequestHeaderError, client_request.search_users_by_username_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.team_user_profile_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.authentication_data)
        self.assertRaises(MissingRequestHeaderError, client_request.inbox_data)
        self.assertRaises(MissingRequestHeaderError, client_request.chat_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.new_team_data)
        self.assertRaises(MissingRequestHeaderError, client_request.add_user_team_data)
        self.assertRaises(MissingRequestHeaderError, client_request.team_invite_data)
        self.assertRaises(MissingRequestHeaderError, client_request.accept_team_invite_data)
        self.assertRaises(MissingRequestHeaderError, client_request.change_role_data, None)
        self.assertRaises(MissingRequestHeaderError, client_request.team_authentication_data, None)
        self.assertRaises(MissingRequestHeaderError, client_request.delete_user_team_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.team_update_data, None)
        self.assertRaises(MissingRequestHeaderError, client_request.new_channel_data)
        self.assertRaises(MissingRequestHeaderError, client_request.channel_invitation_data)
        self.assertRaises(MissingRequestHeaderError, client_request.channel_registration_data)
        self.assertRaises(MissingRequestHeaderError, client_request.delete_user_channel_data, None, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.channel_authentication_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.channel_update_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.add_forbidden_word_data)
        self.assertRaises(MissingRequestHeaderError, client_request.delete_forbidden_word_data, None, None)
