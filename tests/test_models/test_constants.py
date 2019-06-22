import unittest
from unittest.mock import MagicMock

from models.constants import TeamRoles
from models.constants import UserRoles

import sys
sys.modules["logging"].getLogger = MagicMock()


class RolesTestCase(unittest.TestCase):

    def test_team_member_is_not_team_admin(self):
        user_role = TeamRoles.MEMBER.value
        self.assertFalse(TeamRoles.is_team_moderator(user_role))

    def test_team_moderator_is_team_admin(self):
        user_role = TeamRoles.MODERATOR.value
        self.assertTrue(TeamRoles.is_team_moderator(user_role))

    def test_team_creator_is_team_admin(self):
        user_role = TeamRoles.CREATOR.value
        self.assertTrue(TeamRoles.is_team_moderator(user_role))

    def test_superuser_is_team_admin(self):
        user_role = UserRoles.ADMIN.value
        self.assertTrue(TeamRoles.is_team_moderator(user_role))

    def test_team_member_is_not_team_creator(self):
        user_role = TeamRoles.MEMBER.value
        self.assertFalse(TeamRoles.is_team_creator(user_role))

    def test_team_moderator_is_not_team_creator(self):
        user_role = TeamRoles.MODERATOR.value
        self.assertFalse(TeamRoles.is_team_creator(user_role))

    def test_team_creator_is_team_creator(self):
        user_role = TeamRoles.CREATOR.value
        self.assertTrue(TeamRoles.is_team_creator(user_role))

    def test_superuser_is_not_team_creator(self):
        user_role = UserRoles.ADMIN.value
        self.assertFalse(TeamRoles.is_team_creator(user_role))

    def test_team_member_has_not_higher_role_than_any_other_member(self):
        member_role = TeamRoles.MEMBER.value
        moderator_role = TeamRoles.MODERATOR.value
        creator_role = TeamRoles.CREATOR.value
        admin_role = UserRoles.ADMIN.value
        self.assertFalse(TeamRoles.is_higher_role(member_role, member_role))
        self.assertFalse(TeamRoles.is_higher_role(member_role, moderator_role))
        self.assertFalse(TeamRoles.is_higher_role(member_role, creator_role))
        self.assertFalse(TeamRoles.is_higher_role(member_role, admin_role))

    def test_team_moderator_has_higher_role_than_team_member(self):
        member_role = TeamRoles.MEMBER.value
        moderator_role = TeamRoles.MODERATOR.value
        creator_role = TeamRoles.CREATOR.value
        admin_role = UserRoles.ADMIN.value
        self.assertTrue(TeamRoles.is_higher_role(moderator_role, member_role))
        self.assertFalse(TeamRoles.is_higher_role(moderator_role, moderator_role))
        self.assertFalse(TeamRoles.is_higher_role(moderator_role, creator_role))
        self.assertFalse(TeamRoles.is_higher_role(moderator_role, admin_role))

    def test_team_creator_has_higher_role_than_team_member_and_moderator(self):
        member_role = TeamRoles.MEMBER.value
        moderator_role = TeamRoles.MODERATOR.value
        creator_role = TeamRoles.CREATOR.value
        admin_role = UserRoles.ADMIN.value
        self.assertTrue(TeamRoles.is_higher_role(creator_role, member_role))
        self.assertTrue(TeamRoles.is_higher_role(creator_role, moderator_role))
        self.assertFalse(TeamRoles.is_higher_role(creator_role, creator_role))
        self.assertFalse(TeamRoles.is_higher_role(creator_role, admin_role))

    def test_superuser_has_higher_role_than_everybody_else_but_other_superuser(self):
        member_role = TeamRoles.MEMBER.value
        moderator_role = TeamRoles.MODERATOR.value
        creator_role = TeamRoles.CREATOR.value
        admin_role = UserRoles.ADMIN.value
        self.assertTrue(TeamRoles.is_higher_role(admin_role, member_role))
        self.assertTrue(TeamRoles.is_higher_role(admin_role, moderator_role))
        self.assertTrue(TeamRoles.is_higher_role(admin_role, creator_role))
        self.assertFalse(TeamRoles.is_higher_role(admin_role, admin_role))

    def test_user_creator_comparison_works_properly(self):
        user1_creator = True
        user2_creator = False
        self.assertTrue(TeamRoles.is_channel_creator(user1_creator))
        self.assertFalse(TeamRoles.is_channel_creator(user2_creator))
