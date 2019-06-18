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

    @classmethod
    def to_password_recovery(cls, recovery):
        return PasswordRecoveryTableEntry(
            user_id=recovery.user_id,
            token=recovery.token
        )

    @classmethod
    def to_message(cls, message):
        return MessageTableEntry(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            team_id=message.team_id,
            content=message.content,
            send_type=message.send_type,
            message_type=message.message_type
        )

    @classmethod
    def to_chat(cls, chat):
        return ChatTableEntry(
            user_id=chat.user_id,
            chat_id=chat.chat_id,
            team_id=chat.team_id,
            unseen_offset=chat.offset
        )

    @classmethod
    def to_mention(cls, mention):
        return MentionsByMessagesTableEntry(
            message_id=mention.message_id,
            client_id=mention.client_id
        )

    @classmethod
    def to_team_invite(cls, invitation):
        return TeamsInvitesTableEntry(
            team_id=invitation.team_id,
            email=invitation.email,
            invite_token=invitation.token
        )

    @classmethod
    def to_word(cls, word):
        return ForbiddenWordTableEntry(
            word=word.word,
            team_id=word.team_id
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
        ) if user_entry is not None else None

    @classmethod
    def to_public_users(cls, users_entries):
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
        ) if password_entry is not None else None

    @classmethod
    def to_team_user(cls, table_entry):
        if table_entry is None:
            return None

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
                creator_id=channel_entry.creator,
                visibility=channel_entry.visibility,
                description=channel_entry.description,
                welcome_message=channel_entry.welcome_message
            )]
        return channels

    @classmethod
    def to_channel_user(cls, table_entry):
        if table_entry is None:
            return None

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
        user.is_channel_creator = table_entry.creator == table_entry.user_id
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

    @classmethod
    def to_user_in_channel(cls, user_channel_entry):
        return ChannelUser(
            user_id=user_channel_entry.user_id,
            channel_id=user_channel_entry.channel_id
        ) if user_channel_entry is not None else None

    @classmethod
    def to_user_in_team(cls, user_team_entry):
        return TeamUser(
            user_id=user_team_entry.user_id,
            team_id=user_team_entry.team_id
        ) if user_team_entry is not None else None

    @classmethod
    def to_direct_messages_previews(cls, last_messages):
        preview_messages = []
        for last_message in last_messages:
            preview_messages += [
                PreviewDirectMessage(
                    message_id=last_message.message_id,
                    sender_id=last_message.sender_id,
                    receiver_id=last_message.receiver_id,
                    chat_username=last_message.username,
                    chat_first_name=last_message.first_name,
                    chat_last_name=last_message.last_name,
                    chat_picture=last_message.profile_pic,
                    chat_online=last_message.online,
                    content=last_message.content,
                    message_type=last_message.message_type,
                    timestamp=last_message.timestamp,
                    offset=last_message.unseen
                )
            ]

        return preview_messages

    @classmethod
    def to_channel_messages_previews(cls, last_messages):
        preview_messages = []
        for last_message in last_messages:
            preview_messages += [
                PreviewChannelMessage(
                    message_id=last_message.message_id,
                    chat_id=last_message.chat_id,
                    chat_name=last_message.chat_name,
                    chat_picture=None,
                    sender_id=last_message.sender_id,
                    sender_username=last_message.sender_username,
                    sender_first_name=last_message.sender_first_name,
                    sender_last_name=last_message.sender_last_name,
                    content=last_message.content,
                    message_type=last_message.message_type,
                    timestamp=last_message.message_timestamp,
                    offset=last_message.unseen_offset
                )
            ]

        return preview_messages

    @classmethod
    def to_chat(cls, chat_entry):
        return Chat(
            user_id=chat_entry.user_id,
            chat_id=chat_entry.chat_id,
            team_id=chat_entry.team_id,
            offset=chat_entry.unseen_offset
        ) if chat_entry is not None else None

    @classmethod
    def to_messages_chat(cls, messages_entries):
        messages = []
        for message_entry in messages_entries:
            messages += [ChatMessage(
                message_id=message_entry.message_id,
                sender_id=message_entry.sender_id,
                receiver_id=message_entry.receiver_id,
                team_id=message_entry.team_id,
                content=message_entry.content,
                message_type=message_entry.message_type,
                timestamp=message_entry.timestamp,
                username=message_entry.username,
                profile_pic=message_entry.profile_pic,
                first_name=message_entry.first_name,
                last_name=message_entry.last_name,
                online=message_entry.online
            )]

        return messages

    @classmethod
    def to_message_receiver(cls, receiver):
        return MessageReceiver(
            user_id=receiver.user_id if receiver.is_user else None,
            team_id=receiver.team_id,
            is_user=receiver.is_user
        ) if receiver is not None else None

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

    @classmethod
    def to_team_invite(cls, invite):
        return TeamInvite(
            team_id=invite.team_id,
            email=invite.email,
            token=invite.invite_token
        ) if invite is not None else None
