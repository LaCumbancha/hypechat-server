import unittest
from unittest.mock import MagicMock

from dtos.inputs.users import *
from dtos.inputs.teams import *
from dtos.inputs.channels import *
from dtos.inputs.messages import *
from models.request import ClientRequest
from exceptions.exceptions import *
from tests.utils import *


class ClientRequestTestCase(unittest.TestCase):

    def test_new_user_data_without_email_throws_exception(self):
        body_json = {"username": "test", "password": "pass"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_without_username_throws_exception(self):
        body_json = {"password": "pass", "email": "test@gmail.com"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_without_password_throws_exception(self):
        body_json = {"username": "test", "email": "test@gmail.com"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_with_full_data_works_properly(self):
        body_json = {"username": "test", "password": "pass", "email": "test@gmail.com"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.new_user_data(), NewUserDTO)

    def test_app_login_data_without_password_throws_exception(self):
        body_json = {"email": "test@gmail.com"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.login_data)

    def test_app_login_data_without_email_throws_exception(self):
        body_json = {"password": "pass"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.login_data)

    def test_login_data_with_full_data_works_properly(self):
        body_json_app = {"email": "test@gmail.com", "password": "pass"}
        body_json_face = {"facebook_token": "token-test"}
        input_request_app = Request(body_json_app)
        input_request_face = Request(body_json_face)
        client_request_app = ClientRequest(input_request_app)
        client_request_face = ClientRequest(input_request_face)
        self.assertIsInstance(client_request_app.login_data(), LoginDTO)
        self.assertIsInstance(client_request_face.login_data(), LoginDTO)

    def test_recover_password_data_without_email_throws_exception(self):
        recover_json = {}
        input_request = Request(recover_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.recover_data)

    def test_recover_password_data_with_full_data_works_properly(self):
        recover_json = {"email": "test@gmail.com"}
        input_request = Request(recover_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.recover_data(), RecoverPasswordDTO)

    def test_regenerate_password_data_without_email_throws_exception(self):
        body_json = {"recover_token": "test"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.regenerate_data)

    def test_regenerate_password_data_without_recovery_token_throws_exception(self):
        body_json = {"recover_token": "test"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.regenerate_data)

    def test_regenerate_password_data_with_full_data_works_properly(self):
        body_json = {"recover_token": "test", "email": "test@gmail.com"}
        input_request = Request(body_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.regenerate_data(), RegeneratePasswordDTO)

    def test_user_update_with_authentication_header_works_properly(self):
        user_json = {}
        input_request = Request(json=user_json, headers=AUTH_TOKEN_HEADERS)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.user_update(), UserUpdateDTO)

    def test_search_users_by_username_with_authentication_header_works_properly(self):
        input_request = Request(headers=AUTH_TOKEN_HEADERS)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.search_users_data(ANY, ANY), SearchUsersDTO)

    def test_secure_actions_without_authentication_token_throws_exception(self):
        input_request = Request(EMPTY_DICTIONARY)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestHeaderError, client_request.user_update)
        self.assertRaises(MissingRequestHeaderError, client_request.search_users_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.search_user_by_id, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.authentication_data)
        self.assertRaises(MissingRequestHeaderError, client_request.inbox_data)
        self.assertRaises(MissingRequestHeaderError, client_request.chat_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.new_team_data)
        self.assertRaises(MissingRequestHeaderError, client_request.add_data)
        self.assertRaises(MissingRequestHeaderError, client_request.invite_data)
        self.assertRaises(MissingRequestHeaderError, client_request.accept_invite)
        self.assertRaises(MissingRequestHeaderError, client_request.change_role, None)
        self.assertRaises(MissingRequestHeaderError, client_request.team_authentication, None)
        self.assertRaises(MissingRequestHeaderError, client_request.delete_user_team_data, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.team_update, None)
        self.assertRaises(MissingRequestHeaderError, client_request.new_channel_data)
        self.assertRaises(MissingRequestHeaderError, client_request.channel_invitation_data)
        self.assertRaises(MissingRequestHeaderError, client_request.channel_registration_data)
        self.assertRaises(MissingRequestHeaderError, client_request.delete_user_channel, None, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.channel_authentication, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.channel_update, None, None)
        self.assertRaises(MissingRequestHeaderError, client_request.add_forbidden_word)
        self.assertRaises(MissingRequestHeaderError, client_request.delete_forbidden_word, None, None)
