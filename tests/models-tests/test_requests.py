import unittest
from unittest.mock import MagicMock

from dtos.inputs.users import *
from models.request import ClientRequest
from exceptions.exceptions import *
from tests.utils import *


class ClientRequestTestCase(unittest.TestCase):

    def test_new_user_data_without_username_throws_exception(self):
        new_user_json = {
            "password": "pass",
            "email": "test@gmail.com"
        }

        input_request = Request(new_user_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_without_password_throws_exception(self):
        new_user_json = {
            "username": "test",
            "email": "test@gmail.com"
        }

        input_request = Request(new_user_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_without_email_throws_exception(self):
        new_user_json = {
            "username": "test",
            "password": "pass"
        }

        input_request = Request(new_user_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_with_email_password_and_username_works_properly(self):
        new_user_json = {
            "username": "test",
            "password": "pass",
            "email": "test@gmail.com"
        }

        input_request = Request(new_user_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.new_user_data(), NewUserDTO)

    def test_login_data_without_email_and_facebook_token_throws_exception(self):
        login_json = {
            "password": "pass"
        }

        input_request = Request(login_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.login_data)

    def test_login_data_without_password_and_facebook_token_throws_exception(self):
        login_json = {
            "email": "test@gmail.com"
        }

        input_request = Request(login_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.login_data)

    def test_login_data_with_email_and_password_works_properly(self):
        login_json = {
            "email": "test@gmail.com",
            "password": "pass"
        }

        input_request = Request(login_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.login_data(), LoginDTO)

    def test_login_data_with_facebook_token_works_properly(self):
        login_json = {
            "facebook_token": "token-test"
        }

        input_request = Request(login_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.login_data(), LoginDTO)

    def test_recover_data_without_email_throws_exception(self):
        recover_json = {}

        input_request = Request(recover_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.recover_data)

    def test_recover_data_with_works_properly(self):
        recover_json = {
            "email": "test@gmail.com"
        }

        input_request = Request(recover_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.recover_data(), RecoverPasswordDTO)

    def test_regenerate_data_without_email_throws_exception(self):
        regenerate_json = {
            "recover_token": "test"
        }

        input_request = Request(regenerate_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.regenerate_data)

    def test_regenerate_data_without_recover_token_throws_exception(self):
        regenerate_json = {
            "email": "test@gmail.com"
        }

        input_request = Request(regenerate_json)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.regenerate_data)

    def test_recover_data_with_email_and_recover_token_works_properly(self):
        regenerate_json = {
            "recover_token": "test",
            "email": "test@gmail.com"
        }

        input_request = Request(regenerate_json)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.regenerate_data(), RegeneratePasswordDTO)







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
