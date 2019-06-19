from tables.teams import TeamTableEntry, TeamsInvitesTableEntry, ForbiddenWordTableEntry
from tables.users import UsersByTeamsTableEntry

from dtos.models.teams import Team, TeamUser, TeamInvite, ForbiddenWord
from dtos.models.users import PublicUser
from dtos.models.channels import Channel, ChannelCreator


class TeamDatabaseMapper:

    @classmethod
    def to_team(cls, team):
        return TeamTableEntry(
            team_name=team.name,
            picture=team.picture,
            location=team.location,
            description=team.description,
            welcome_message=team.welcome_message
        )

    @classmethod
    def to_team_user(cls, team_user):
        return UsersByTeamsTableEntry(
            user_id=team_user.user_id,
            team_id=team_user.team_id,
            role=team_user.role
        )

    @classmethod
    def to_team_invite(cls, invitation):
        return TeamsInvitesTableEntry(
            team_id=invitation.team_id,
            email=invitation.email,
            invite_token=invitation.token
        )

    @classmethod
    def to_forbidden_word(cls, word):
        return ForbiddenWordTableEntry(
            word=word.word,
            team_id=word.team_id
        )


class TeamModelMapper:

    @classmethod
    def to_team(cls, team_entry):
        return Team(
            team_id=team_entry.team_id,
            name=team_entry.team_name,
            picture=team_entry.picture,
            location=team_entry.location,
            description=team_entry.description,
            welcome_message=team_entry.welcome_message
        ) if team_entry is not None else None

    @classmethod
    def to_user_in_team(cls, user_team_entry):
        return TeamUser(
            user_id=user_team_entry.user_id,
            team_id=user_team_entry.team_id
        ) if user_team_entry is not None else None

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
    def to_team_members(cls, members_entries):
        users = []
        for member_entry in members_entries:
            user = PublicUser(
                user_id=member_entry.user_id,
                username=member_entry.username,
                email=member_entry.email,
                first_name=member_entry.first_name,
                last_name=member_entry.last_name,
                profile_pic=member_entry.profile_pic,
                role=member_entry.role,
                online=member_entry.online
            )
            user.team_id = member_entry.team_id
            user.team_role = member_entry.team_role
            users += [user]
        return users

    @classmethod
    def to_team_channels(cls, channels_entries):
        channels = []
        for channel_entry in channels_entries:
            channels += [Channel(
                channel_id=channel_entry.channel_id,
                team_id=channel_entry.team_id,
                name=channel_entry.name,
                creator=ChannelCreator(
                    user_id=channel_entry.user_id,
                    username=channel_entry.username,
                    first_name=channel_entry.first_name,
                    last_name=channel_entry.last_name
                ),
                visibility=channel_entry.visibility,
                description=channel_entry.description,
                welcome_message=channel_entry.welcome_message
            )]
        return channels

    @classmethod
    def to_team_invite(cls, invite):
        return TeamInvite(
            team_id=invite.team_id,
            email=invite.email,
            token=invite.invite_token
        ) if invite is not None else None

    @classmethod
    def to_forbidden_word(cls, word):
        return ForbiddenWord(
            word_id=word.id,
            word=word.word,
            team_id=word.team_id
        ) if word is not None else None

    @classmethod
    def to_forbidden_words(cls, words_entries):
        words = []
        for word_entry in words_entries:
            words += [ForbiddenWord(
                word_id=word_entry.id,
                word=word_entry.word,
                team_id=word_entry.team_id
            )]

        return words
