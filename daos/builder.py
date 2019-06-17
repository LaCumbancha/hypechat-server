from dtos.models.users import *
from dtos.models.teams import *
from dtos.models.channels import *
from dtos.models.messages import *

from tables.users import *
from tables.teams import *
from tables.channels import *
from tables.messages import *

from models.constants import ChannelVisibilities, SendMessageType, TeamRoles


class TableEntryBuilder:

    @classmethod
    def to_user(cls, user):
        return UserTableEntry(
            user_id=user.id,
            facebook_id=user.facebook_id,
            username=user.username,
            email=user.email,
            password=user.password,
            first_name=user.first_name,
            last_name=user.last_name,
            profile_pic=user.profile_pic,
            role=user.role,
            auth_token=user.token,
            online=user.online
        )

    @classmethod
    def to_password_recovery(cls, recovery):
        return PasswordRecoveryTableEntry(
            user_id=recovery.user_id,
            token=recovery.token
        )

    @classmethod
    def to_mention(cls, mention):
        return MentionsByMessagesTableEntry(
            message_id=mention.message_id,
            client_id=mention.client_id
        )


class ModelBuilder:

    @classmethod
    def to_user(cls, user_entry):
        return User(
            user_id=user_entry.user_id,
            role=user_entry.role,
            online=user_entry.online,
            token=user_entry.auth_token,
            first_name=user_entry.first_name,
            last_name=user_entry.last_name,
            profile_pic=user_entry.profile_pic,
            password=user_entry.password,
            email=user_entry.email,
            username=user_entry.username,
            facebook_id=user_entry.facebook_id
        )

    @classmethod
    def to_team(cls, team_entry):
        return Team(
            team_id=team_entry.team_id,
            name=team_entry.team_name,
            picture=team_entry.picture,
            location=team_entry.location,
            description=team_entry.description,
            welcome_message=team_entry.welcome_message
        )

    @classmethod
    def to_channel(cls, channel_entry):
        return Channel(
            channel_id=channel_entry.channel_id,
            team_id=channel_entry.team_id,
            name=channel_entry.name,
            creator_id=channel_entry.creator,
            visibility=channel_entry.visibility,
            description=channel_entry.description,
            welcome_message=channel_entry.welcome_message
        )

    @classmethod
    def to_teams(cls, team_entries):
        teams = []
        for team_entry in team_entries:
            teams += [Team(
                team_id=team_entry.team_id,
                name=team_entry.team_name,
                picture=team_entry.picture,
                location=team_entry.location,
                description=team_entry.description,
                welcome_message=team_entry.welcome_message,
                role=team_entry.role
            )]

        return teams

    @classmethod
    def to_password_recovery(cls, password_entry):
        return PasswordRecovery(
            user_id=password_entry.user_id,
            token=password_entry.token
        )

    @classmethod
    def to_team_user(cls, table_entry):
        user = PublicUser(
            user_id=table_entry.user_id,
            username=table_entry.username,
            email=table_entry.email,
            first_name=table_entry.first_name,
            last_name=table_entry.last_name,
            profile_pic=table_entry.profile_pic,
            role=table_entry.user_role,
            online=table_entry.online
        )
        user.team_id = table_entry.team_id
        user.team_role = table_entry.team_role
        return user

    @classmethod
    def to_channel_user(cls, table_entry):
        user = PublicUser(
            user_id=table_entry.user_id,
            username=table_entry.username,
            email=table_entry.email,
            first_name=table_entry.first_name,
            last_name=table_entry.last_name,
            profile_pic=table_entry.profile_pic,
            online=table_entry.online,
            role=table_entry.role
        )
        user.team_id = table_entry.team_id
        user.channel_id = table_entry.channel_id
        user.is_channel_creator = channel_user_entry.creator == table_entry.user_id
        return user

    @classmethod
    def to_user_with_teams(cls, table_entries):
        user_with_teams = []
        for table_entry in table_entries:
            user = PublicUser(
                user_id=table_entry.user_id,
                username=table_entry.username,
                email=table_entry.email,
                first_name=table_entry.first_name,
                last_name=table_entry.last_name,
                profile_pic=table_entry.profile_pic,
                online=True,
                role=table_entry.user_role
            )
            user.team_id = table_entry.team_id
            user.team_name = table_entry.team_name
            user.team_picture = table_entry.picture
            user.team_location = table_entry.location
            user.team_description = table_entry.description
            user.team_message = table_entry.welcome_message
            user.team_role = table_entry.team_role
            user_with_teams += [user]
        return user_with_teams

    @classmethod
    def to_mentions(cls, mentions_entries):
        mentions = []
        for mention_entry in mentions_entries:
            mentions += [ClientMention(
                user_id=mention_entry.user_id,
                username=mention_entry.username,
                first_name=mention_entry.first_name,
                last_name=mention_entry.last_name
            )]
        return mentions
