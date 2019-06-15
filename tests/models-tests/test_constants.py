import unittest
from unittest.mock import MagicMock

from models.constants import TeamRoles
from models.constants import UserRoles


class RolesTestCase(unittest.TestCase):

    def test_team_member_is_not_team_admin(self):
        user = MagicMock()
        user.role = TeamRoles.MEMBER.value
        self.assertFalse(TeamRoles.is_team_admin(user))

    def test_team_moderator_is_team_admin(self):
        user = MagicMock()
        user.role = TeamRoles.MODERATOR.value
        self.assertTrue(TeamRoles.is_team_admin(user))

    def test_team_creator_is_team_admin(self):
        user = MagicMock()
        user.role = TeamRoles.CREATOR.value
        self.assertTrue(TeamRoles.is_team_admin(user))

    def test_superuser_is_team_admin(self):
        user = MagicMock()
        user.role = UserRoles.ADMIN.value
        self.assertTrue(TeamRoles.is_team_admin(user))

    def test_team_member_is_not_team_creator(self):
        user = MagicMock()
        user.role = TeamRoles.MEMBER.value
        self.assertFalse(TeamRoles.is_team_creator(user))

    def test_team_moderator_is_not_team_creator(self):
        user = MagicMock()
        user.role = TeamRoles.MODERATOR.value
        self.assertFalse(TeamRoles.is_team_creator(user))

    def test_team_creator_is_team_creator(self):
        user = MagicMock()
        user.role = TeamRoles.CREATOR.value
        self.assertTrue(TeamRoles.is_team_creator(user))

    def test_superuser_is_not_team_creator(self):
        user = MagicMock()
        user.role = UserRoles.ADMIN.value
        self.assertFalse(TeamRoles.is_team_creator(user))

    def test_team_member_has_not_higher_role_than_any_other_member(self):
        member = MagicMock()
        moderator = MagicMock()
        creator = MagicMock()
        admin = MagicMock()
        member.role = TeamRoles.MEMBER.value
        moderator.role = TeamRoles.MODERATOR.value
        creator.role = TeamRoles.CREATOR.value
        admin.role = UserRoles.ADMIN.value
        self.assertFalse(TeamRoles.has_higher_role(member, member))
        self.assertFalse(TeamRoles.has_higher_role(member, moderator))
        self.assertFalse(TeamRoles.has_higher_role(member, creator))
        self.assertFalse(TeamRoles.has_higher_role(member, admin))

    def test_team_moderator_has_higher_role_than_team_member(self):
        member = MagicMock()
        moderator = MagicMock()
        creator = MagicMock()
        admin = MagicMock()
        member.role = TeamRoles.MEMBER.value
        moderator.role = TeamRoles.MODERATOR.value
        creator.role = TeamRoles.CREATOR.value
        admin.role = UserRoles.ADMIN.value
        self.assertTrue(TeamRoles.has_higher_role(moderator, member))
        self.assertFalse(TeamRoles.has_higher_role(moderator, moderator))
        self.assertFalse(TeamRoles.has_higher_role(moderator, creator))
        self.assertFalse(TeamRoles.has_higher_role(moderator, admin))

    def test_team_creator_has_higher_role_than_team_member_and_moderator(self):
        member = MagicMock()
        moderator = MagicMock()
        creator = MagicMock()
        admin = MagicMock()
        member.role = TeamRoles.MEMBER.value
        moderator.role = TeamRoles.MODERATOR.value
        creator.role = TeamRoles.CREATOR.value
        admin.role = UserRoles.ADMIN.value
        self.assertTrue(TeamRoles.has_higher_role(creator, member))
        self.assertTrue(TeamRoles.has_higher_role(creator, moderator))
        self.assertFalse(TeamRoles.has_higher_role(creator, creator))
        self.assertFalse(TeamRoles.has_higher_role(creator, admin))

    def test_superuser_has_higher_role_than_everybody_else_but_other_superuser(self):
        member = MagicMock()
        moderator = MagicMock()
        creator = MagicMock()
        admin = MagicMock()
        member.role = TeamRoles.MEMBER.value
        moderator.role = TeamRoles.MODERATOR.value
        creator.role = TeamRoles.CREATOR.value
        admin.role = UserRoles.ADMIN.value
        self.assertTrue(TeamRoles.has_higher_role(admin, member))
        self.assertTrue(TeamRoles.has_higher_role(admin, moderator))
        self.assertTrue(TeamRoles.has_higher_role(admin, creator))
        self.assertFalse(TeamRoles.has_higher_role(admin, admin))

    def test_user_comparison_by_id_works_properly(self):
        user1_id = 0
        user2_id = 0
        user3_id = 1
        self.assertTrue(TeamRoles.is_channel_creator(user1_id, user2_id))
        self.assertFalse(TeamRoles.is_channel_creator(user1_id, user3_id))
