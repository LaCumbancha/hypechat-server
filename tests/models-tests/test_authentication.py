import unittest
from unittest.mock import MagicMock
from time import sleep

import sys
sys.modules["app"] = MagicMock()
sys.modules["sqlalchemy"] = MagicMock()

from models.authentication import Authenticator


class AuthenticationTestCase(unittest.TestCase):

    def test_different_tokens_generated_for_different_users(self):
        user1_id = 1
        user2_id = 2
        self.assertNotEqual(Authenticator.generate(user1_id), Authenticator.generate(user2_id))

    def test_different_tokens_generated_for_same_user_in_different_times(self):
        user_id = 1
        token1 = Authenticator.generate(user_id)
        sleep(0.05)
        token2 = Authenticator.generate(user_id)
        self.assertNotEqual(token1, token2)

    def test_recovery_tokens_generated_are_different(self):
        self.assertNotEqual(Authenticator.generate_recovery_token(), Authenticator.generate_recovery_token())

    def test_team_invitations_generated_are_different(self):
        self.assertNotEqual(Authenticator.generate_team_invitation(), Authenticator.generate_team_invitation())
