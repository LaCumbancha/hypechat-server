import unittest
from unittest.mock import MagicMock

from dtos.inputs.users import *
from models.request import ClientRequest
from exceptions.exceptions import *

EMPTY_LIST = []


class Request:

    def __init__(self, json=None):
        self.json = json
        self.is_json = json is not None
        self.headers = []

    def get_json(self):
        return self.json


class ClientRequestTestCase(unittest.TestCase):

    def test_new_user_data_without_username_throws_exception(self):
        new_user_json = {
            "password": "pass",
            "email": "test@gmail.com"
        }

        input_request = Request(new_user_json)
        input_request.headers = MagicMock(return_value=EMPTY_LIST)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_without_password_throws_exception(self):
        new_user_json = {
            "username": "test",
            "email": "test@gmail.com"
        }

        input_request = Request(new_user_json)
        input_request.headers = MagicMock(return_value=EMPTY_LIST)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_without_email_throws_exception(self):
        new_user_json = {
            "username": "test",
            "password": "pass"
        }

        input_request = Request(new_user_json)
        input_request.headers = MagicMock(return_value=EMPTY_LIST)
        client_request = ClientRequest(input_request)
        self.assertRaises(MissingRequestParameterError, client_request.new_user_data)

    def test_new_user_data_with_email_password_username_works_properly(self):
        new_user_json = {
            "username": "test",
            "password": "pass",
            "email": "test@gmail.com"
        }

        input_request = Request(new_user_json)
        input_request.headers = MagicMock(return_value=EMPTY_LIST)
        client_request = ClientRequest(input_request)
        self.assertIsInstance(client_request.new_user_data(), NewUserDTO)
