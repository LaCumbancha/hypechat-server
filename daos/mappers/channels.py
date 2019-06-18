from tables.channels import ChannelTableEntry
from tables.users import UsersByChannelsTableEntry

from dtos.models.channels import Channel, ChannelUser
from dtos.models.users import PublicUser


class ChannelDatabaseMapper:

    @classmethod
    def to_channel(cls, channel):
        return ChannelTableEntry(
            channel_id=channel.channel_id,
            team_id=channel.team_id,
            creator=channel.creator_id,
            name=channel.name,
            visibility=channel.visibility,
            description=channel.description,
            welcome_message=channel.welcome_message
        )

    @classmethod
    def to_channel_user(cls, channel_user):
        return UsersByChannelsTableEntry(
            user_id=channel_user.user_id,
            channel_id=channel_user.channel_id
        )


class ChannelModelMapper:

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
        ) if channel_entry is not None else None

    @classmethod
    def to_user_in_channel(cls, user_channel_entry):
        return ChannelUser(
            user_id=user_channel_entry.user_id,
            channel_id=user_channel_entry.channel_id
        ) if user_channel_entry is not None else None

    @classmethod
    def to_channel_members(cls, users_entries):
        users = []
        for user_entry in users_entries:
            users += [PublicUser(
                user_id=user_entry.user_id,
                username=user_entry.username,
                email=user_entry.email,
                first_name=user_entry.first_name,
                last_name=user_entry.last_name,
                profile_pic=user_entry.profile_pic,
                role=user_entry.role,
                online=user_entry.online
            )]

        return users
