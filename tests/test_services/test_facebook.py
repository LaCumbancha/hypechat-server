import unittest
from unittest.mock import MagicMock

from exceptions.exceptions import FacebookWrongTokenError
from dtos.model import FacebookUserDTO

'''Mocking environment properties'''
import sys
sys.modules["config"] = MagicMock()
sys.modules["json"] = MagicMock()
sys.modules["requests"] = MagicMock()
sys.modules["os"].getenv = MagicMock(side_effect=lambda key: environment_properties.get(key))
sys.modules["logging"].getLogger = MagicMock()

environment_properties = {
    'FACEBOOK_APP_SECRET': "TEST"
}

from services.facebook import FacebookService


class FacebookServiceTestCase(unittest.TestCase):

    def test_invalid_facebook_token_throws_exception(self):
        user = MagicMock()
        user.facebook_token = "TEST"

        '''Mocked outputs'''
        facebook_data = MagicMock()
        facebook_json = MagicMock()
        facebook_json.get().get.return_value = False

        sys.modules["requests"].get.return_value = facebook_data
        sys.modules["json"].loads.return_value = facebook_json
        self.assertRaises(FacebookWrongTokenError, FacebookService.get_user_from_facebook, user)

    def test_valid_facebook_token_returns_facebook_user(self):
        user = MagicMock()
        user.facebook_token = "TEST"

        '''Mocked outputs'''
        facebook_data = MagicMock()
        facebook_json = MagicMock()
        facebook_json.get().get.return_value = True

        sys.modules["requests"].get.return_value = facebook_data
        sys.modules["json"].loads.return_value = facebook_json
        self.assertIsInstance(FacebookService.get_user_from_facebook(user), FacebookUserDTO)
