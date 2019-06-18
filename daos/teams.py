from app import db
from sqlalchemy import and_, literal

from daos.database import DatabaseClient
from daos.mappers.teams import TeamDatabaseMapper, TeamModelMapper

from tables.users import UserTableEntry, UsersByTeamsTableEntry
from tables.teams import TeamTableEntry, TeamsInvitesTableEntry, ForbiddenWordTableEntry
from tables.channels import ChannelTableEntry


class TeamDatabaseClient:

    @classmethod
    def add_team(cls, team):
        team_entry = TeamDatabaseMaper.to_team(team)
        DatabaseClient.add(team_entry)
        return TeamModelMapper.to_team(team_entry)

    @classmethod
    def add_team_user(cls, team_user):
        team_user_entry = TeamDatabaseMaper.to_team_user(team_user)
        DatabaseClient.add(team_user_entry)

    @classmethod
    def add_invite(cls, invite):
        invite_entry = TeamDatabaseMaper.to_team_invite(invite)
        DatabaseClient.add(invite_entry)

    @classmethod
    def add_forbidden_word(cls, word):
        word_entry = TeamDatabaseMaper.to_forbidden_word(word)
        DatabaseClient.add(word_entry)

    @classmethod
    def delete_team(cls, team):
        db.session.query(TeamTableEntry).filter(TeamTableEntry.team_id == team.id).delete()

    @classmethod
    def delete_team_user(cls, user):
        db.session.query(UsersByTeamsTableEntry).filter(
            UsersByTeamsTableEntry.user_id == user.user_id,
            UsersByTeamsTableEntry.team_id == user.team_id
        ).delete()

    @classmethod
    def delete_invite(cls, invite):
        db.session.query(TeamsInvitesTableEntry).filter(
            TeamsInvitesTableEntry.team_id == invite.team_id,
            TeamsInvitesTableEntry.email == invite.email
        ).delete()

    @classmethod
    def delete_forbidden_word(cls, word):
        db.session.query(ForbiddenWordTableEntry).filter(
            ForbiddenWordTableEntry.team_id == word.team_id,
            ForbiddenWordTableEntry.id == word.id
        ).delete()

    @classmethod
    def update_team(cls, team):
        team_entry = db.session.query(TeamTableEntry).filter(TeamTableEntry.team_id == team.id).one_or_none()
        team_entry.team_name = team.name
        team_entry.picture = team.picture
        team_entry.location = team.location
        team_entry.description = team.description
        team_entry.welcome_message = team.welcome_message
        DatabaseClient.add(team_entry)
        return TeamModelMapper.to_team(team_entry)

    @classmethod
    def update_team_user(cls, team_user):
        team_user_entry = db.session.query(UsersByTeamsTableEntry).filter(
            UsersByTeamsTableEntry.user_id == team_user.user_id,
            UsersByTeamsTableEntry.team_id == team_user.team_id
        ).one_or_none()
        team_user_entry.role = team_user.role
        DatabaseClient.add(team_user_entry)

    @classmethod
    def get_team_by_id(cls, team_id):
        team_entry = db.session.query(TeamTableEntry).filter(TeamTableEntry.team_id == team_id).one_or_none()
        return TeamModelMapper.to_team(team_entry)

    @classmethod
    def get_team_by_name(cls, team_name):
        team_entry = db.session.query(TeamTableEntry).filter(TeamTableEntry.team_name == team_name).one_or_none()
        return TeamModelMapper.to_team(team_entry)

    @classmethod
    def get_user_teams_by_user_id(cls, user_id, is_admin=False):
        if is_admin:
            team_entry = db.session.query(
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                literal(None).label("role")
            ).all()
        else:
            team_entry = db.session.query(
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                UsersByTeamsTableEntry.role
            ).join(
                UsersByTeamsTableEntry,
                and_(
                    UsersByTeamsTableEntry.user_id == user_id,
                    UsersByTeamsTableEntry.team_id == TeamTableEntry.team_id
                )
            ).all()
        return TeamModelMapper.to_teams(team_entry)

    @classmethod
    def get_user_in_team_by_ids(cls, user_id, team_id):
        team_user = db.session.query(UsersByTeamsTableEntry).filter(
            UsersByTeamsTableEntry.user_id == user_id,
            UsersByTeamsTableEntry.team_id == team_id
        ).one_or_none()
        return TeamModelMapper.to_user_in_team(team_user)

    @classmethod
    def get_user_in_team_by_email(cls, email, team_id):
        team_user = db.session.query(UsersByTeamsTableEntry).join(
            UserTableEntry,
            and_(
                UsersByTeamsTableEntry.team_id == team_id,
                UserTableEntry.user_id == UsersByTeamsTableEntry.user_id,
                UserTableEntry.email == email
            )
        ).one_or_none()
        return TeamModelMapper.to_user_in_team(team_user)

    @classmethod
    def get_all_team_users_by_team_id(cls, team_id):
        users = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UserTableEntry.role,
            UsersByTeamsTableEntry.team_id,
            UsersByTeamsTableEntry.role.label("team_role")
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UserTableEntry.user_id == UsersByTeamsTableEntry.user_id,
                UsersByTeamsTableEntry.team_id == team_id
            )
        ).all()
        return TeamModelMapper.to_team_members(users)

    @classmethod
    def get_all_team_users_by_likely_name(cls, team_id, username):
        users = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online,
            UserTableEntry.role,
            UsersByTeamsTableEntry.team_id,
            UsersByTeamsTableEntry.role.label("team_role")
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == UserTableEntry.user_id,
                UsersByTeamsTableEntry.team_id == team_id,
                UserTableEntry.username.like(f"%{username}%")
            )
        ).all()
        return TeamModelMapper.to_team_members(users)

    @classmethod
    def get_all_team_channels_by_team_id(cls, team_id):
        channels = db.session.query(ChannelTableEntry).filter(ChannelTableEntry.team_id == team_id).all()
        return TeamModelMapper.to_team_channels(channels)

    @classmethod
    def get_team_invite(cls, team_id, email):
        invite = db.session.query(TeamsInvitesTableEntry).filter(
            TeamsInvitesTableEntry.team_id == team_id,
            TeamsInvitesTableEntry.email == email
        ).one_or_none()
        return TeamModelMapper.to_team_invite(invite)

    @classmethod
    def get_team_invite_by_token(cls, token, email):
        invite = db.session.query(TeamsInvitesTableEntry).filter(
            TeamsInvitesTableEntry.invite_token == token,
            TeamsInvitesTableEntry.email == email
        ).one_or_none()
        return TeamModelMapper.to_team_invite(invite)

    @classmethod
    def get_forbidden_word_by_word(cls, team_id, word):
        word = db.session.query(ForbiddenWordTableEntry).filter(
            ForbiddenWordTableEntry.team_id == team_id,
            ForbiddenWordTableEntry.word == word
        ).one_or_none()
        return TeamModelMapper.to_forbidden_word(word)

    @classmethod
    def get_forbidden_word_by_id(cls, team_id, word_id):
        word = db.session.query(ForbiddenWordTableEntry).filter(
            ForbiddenWordTableEntry.team_id == team_id,
            ForbiddenWordTableEntry.id == word_id
        ).one_or_none()
        return TeamModelMapper.to_forbidden_word(word)

    @classmethod
    def get_forbidden_words_from_team(cls, team_id):
        words = db.session.query(ForbiddenWordTableEntry).filter(
            ForbiddenWordTableEntry.team_id == team_id
        ).all()
        return TeamModelMapper.to_forbidden_words(words)
