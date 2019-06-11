from app import db
from dtos.responses.channels import *
from dtos.responses.clients import SuccessfulUsersListResponse
from models.authentication import Authenticator
from services.notifications import NotificationService
from tables.users import UsersByChannelsTableEntry, UsersByTeamsTableEntry, UserTableEntry
from tables.channels import *
from tables.messages import *
from sqlalchemy import exc, and_

import logging


class ChannelService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_channel(cls, creation_data):
        user = Authenticator.authenticate_team(creation_data.authentication)
        new_client = ClientTableEntry()

        try:
            db.session.add(new_client)
            db.session.flush()
            new_channel = ChannelTableEntry(
                channel_id=new_client.client_id,
                team_id=user.team_id,
                creator=user.user_id,
                name=creation_data.name,
                visibility=creation_data.visibility or ChannelVisibilities.PUBLIC.value,
                description=creation_data.description,
                welcome_message=creation_data.welcome_message
            )
            db.session.add(new_channel)
            db.session.flush()
            new_user_by_channel = UsersByChannelsTableEntry(
                user_id=user.user_id,
                channel_id=new_channel.channel_id
            )
            db.session.add(new_user_by_channel)
            db.session.flush()
            db.session.commit()
            cls.logger().info(f"Channel #{new_channel.channel_id} created in team {user.team_id}.")
            cls.logger().info(
                f"User #{user.user_id} assigned as channel #{new_channel.channel_id} creator.")
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(TeamTableEntry).filter(ChannelTableEntry.name == creation_data.name).first():
                cls.logger().info(
                    f"Failing to create channel {creation_data.name}. Name already in use for other channel.")
                return BadRequestChannelMessageResponse(
                    f"Channel {creation_data.name} already in use for other channel.",
                    TeamResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().error(f"Failing to create channel {creation_data.name}.")
                return UnsuccessfulChannelMessageResponse("Couldn't create channel.")
        else:
            return SuccessfulChannelResponse(new_channel, TeamResponseStatus.CREATED.value)

    @classmethod
    def add_member(cls, invitation_data):
        user = Authenticator.authenticate_channel(invitation_data.authentication, TeamRoles.is_channel_creator)

        if not db.session.query(UserTableEntry).filter(
                UserTableEntry.user_id == invitation_data.user_invited_id
        ).one_or_none():
            cls.logger().info(f"Trying to add user an nonexistent user to channel"
                              f"{invitation_data.authentication.channel_id}.")
            return BadRequestChannelMessageResponse(
                "Invited user not found!", UserResponseStatus.USER_NOT_FOUND.value)

        if not db.session.query(UsersByTeamsTableEntry).filter(
                UsersByTeamsTableEntry.user_id == invitation_data.user_invited_id,
                UsersByTeamsTableEntry.team_id == invitation_data.authentication.team_id
        ).one_or_none():
            cls.logger().info(f"Trying to add user {invitation_data.user_invited_id} to channel"
                              f"{invitation_data.authentication.channel_id}, but it's not part of the team #"
                              f"{invitation_data.authentication.team_id}.")
            return BadRequestChannelMessageResponse(
                "User not part of the team!", TeamResponseStatus.USER_NOT_MEMBER.value)

        try:
            new_user_by_channel = UsersByChannelsTableEntry(
                user_id=invitation_data.user_invited_id,
                channel_id=invitation_data.authentication.channel_id
            )
            db.session.add(new_user_by_channel)
            db.session.commit()
            NotificationService.notify_channel_invitation(new_user_by_channel, user.user_id)
            cls.logger().info(f"User #{invitation_data.user_invited_id} added to channel "
                              f"#{invitation_data.authentication.channel_id} by {user.username}.")
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(UsersByChannelsTableEntry).filter(
                    UsersByChannelsTableEntry.user_id == invitation_data.user_invited_id,
                    UsersByChannelsTableEntry.channel_id == invitation_data.authentication.channel_id
            ).one_or_none():
                cls.logger().info(
                    f"Failing to create add user #{invitation_data.user_invited_id} to channel "
                    f"{invitation_data.authentication.channel_id}. The user is already part of the channel.")
                return BadRequestChannelMessageResponse(f"User already registered in channel.",
                                                        TeamResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().error(f"Failing to add user #{invitation_data.user_invited_id} to channel"
                                   f"{invitation_data.authentication.channel_id}.")
                return UnsuccessfulChannelMessageResponse("Couldn't add user to channel.")
        else:
            return SuccessfulChannelMessageResponse("User added!", ChannelResponseStatus.ADDED.value)

    @classmethod
    def join_channel(cls, registration_data):
        user = Authenticator.authenticate_team(registration_data.authentication)

        channel = db.session().query(ChannelTableEntry).filter(
            ChannelTableEntry.channel_id == registration_data.channel_id
        ).one_or_none()

        if not channel:
            cls.logger().info(
                f"User {user.user_id} attempting to join channel #{registration_data.channel_id}, which does not exist.")
            return BadRequestChannelMessageResponse("Channel not found.", ChannelResponseStatus.CHANNEL_NOT_FOUND.value)

        if channel.team_id != user.team_id:
            cls.logger().info(
                f"User {user.user_id} from team {user.team_id} attempting to join channel #{channel.channel_id},"
                f"but it's in team {channel.team_id}.")
            return BadRequestChannelMessageResponse("Other team's channel.", ChannelResponseStatus.OTHER_TEAM.value)

        if channel.visibility == ChannelVisibilities.PRIVATE.value:
            cls.logger().info(
                f"User {user.user_id} attempting to join channel #{channel.channel_id}, which is private.")
            return BadRequestChannelMessageResponse("Private channel!", ChannelResponseStatus.PRIVATE_VISIBILITY.value)

        user_channel = UsersByChannelsTableEntry(
            user_id=user.user_id,
            channel_id=channel.channel_id
        )

        try:
            db.session.add(user_channel)
            db.session.commit()
            cls.logger().info(f"User {user.user_id} joined channel #{channel.channel_id}.")
            return SuccessfulChannelResponse(channel, ChannelResponseStatus.JOINED.value)
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"User #{user.user_id} failed at joining channel #{channel.channel_id}.")
            return UnsuccessfulChannelMessageResponse("Couldn't join channel.")

    @classmethod
    def remove_member(cls, delete_data):
        user = Authenticator.authenticate_channel(delete_data.authentication, TeamRoles.is_channel_creator)

        delete_user = db.session.query(UsersByChannelsTableEntry).filter(
            UsersByChannelsTableEntry.user_id == delete_data.delete_id,
            UsersByChannelsTableEntry.channel_id == delete_data.authentication.channel_id
        ).one_or_none()

        if delete_user:
            try:
                db.session.delete(delete_user)
                db.session.commit()
                cls.logger().info(f"User #{delete_user.user_id} removed from channel #{delete_user.channel_id}.")
                return SuccessfulChannelMessageResponse("User removed!", ChannelResponseStatus.REMOVED.value)
            except exc.IntegrityError:
                db.session.rollback()
                cls.logger().error(
                    f"Failed at removing user #{delete_user.user_id} from channel #{delete_user.channel_id}.")
                return UnsuccessfulChannelMessageResponse("Couldn't remove user.")
        else:
            cls.logger().info(f"User {user.user_id} trying to delete user #{delete_data.delete_id} from channel "
                              f"#{delete_data.authentication.channel_id}, but it's not part of it!")
            return BadRequestChannelMessageResponse("User not part of channel!.",
                                                    ChannelResponseStatus.USER_NOT_MEMBER.value)

    @classmethod
    def channel_members(cls, authentication_data):
        user = Authenticator.authenticate_channel(authentication_data)

        members = db.session.query(
            UserTableEntry.user_id,
            UserTableEntry.username,
            UserTableEntry.email,
            UserTableEntry.first_name,
            UserTableEntry.last_name,
            UserTableEntry.profile_pic,
            UserTableEntry.online
        ).join(
            UsersByChannelsTableEntry,
            and_(
                UserTableEntry.user_id == UsersByChannelsTableEntry.user_id,
                UsersByChannelsTableEntry.channel_id == authentication_data.channel_id
            )
        ).all()

        cls.logger().info(
            f"User {user.username} got {len(members)} users from channel #{authentication_data.channel_id}.")
        return SuccessfulUsersListResponse(cls._channel_users_list(members))

    @classmethod
    def _channel_users_list(cls, user_list):
        users = []

        for user in user_list:
            users += [{
                "id": user.user_id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_pic": user.profile_pic,
                "online": user.online
            }]

        return users

    @classmethod
    def leave_channel(cls, user_data):
        user = Authenticator.authenticate_channel(user_data)

        delete_user = db.session.query(UsersByChannelsTableEntry).filter(and_(
            UsersByChannelsTableEntry.user_id == user.user_id,
            UsersByChannelsTableEntry.channel_id == user_data.channel_id
        )).one_or_none()

        try:
            db.session.delete(delete_user)
            db.session.commit()
            cls.logger().info(f"User #{user.user_id} leaved channel #{user_data.channel_id}.")
            return SuccessfulChannelMessageResponse("Channel leaved!", ChannelResponseStatus.REMOVED.value)
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"User #{user.user_id} failing to leave channel #{user_data.channel_id}.")
            return UnsuccessfulTeamMessageResponse("Couldn't leave chanel.")

    @classmethod
    def update_information(cls, update_data):
        user = Authenticator.authenticate_channel(update_data.authentication, TeamRoles.is_channel_creator)
        channel = db.session.query(ChannelTableEntry).filter(
            ChannelTableEntry.channel_id == update_data.authentication.channel_id
        ).one_or_none()

        channel.name = \
            update_data.updated_channel["name"] if "name" in update_data.updated_channel else channel.name
        channel.visibility = \
            update_data.updated_channel["visibility"] if "visibility" in update_data.updated_channel \
                else channel.visibility
        channel.description = \
            update_data.updated_channel["description"] if "description" in update_data.updated_channel \
                else channel.description
        channel.welcome_message = \
            update_data.updated_channel["welcome_message"] if "welcome_message" in update_data.updated_channel \
                else channel.welcome_message

        try:
            db.session.commit()
            cls.logger().info(
                f"Channel {channel.channel_id} information updated by user {user.username}.")
            return SuccessfulChannelResponse(channel, ChannelResponseStatus.UPDATED.value)
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(ChannelTableEntry).filter(
                    ChannelTableEntry.name == update_data.updated_team.get("name")
            ).one_or_none():
                cls.logger().info(f"Trying to update channel {update_data.authentication.channel_id}'s name with " +
                                  f"{update_data.updated_channel.get('name')}, that currently exists.")
                return BadRequestChannelMessageResponse(f"Name {update_data.updated_channel.get('name')}" +
                                                        " is already in use!", TeamResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().error(f"Couldn't update channel {update_data.authentication.channel_id} information.")
                return UnsuccessfulTeamMessageResponse("Couldn't update channel information!")

    @classmethod
    def delete_channel(cls, user_data):
        user = Authenticator.authenticate_channel(user_data)

        channel_messages = db.session.query(MessageTableEntry).filter(
            MessageTableEntry.team_id == user_data.team_id,
            MessageTableEntry.receiver_id == user_data.channel_id
        )

        channel_chats = db.session.query(ChatTableEntry).filter(
            ChatTableEntry.chat_id == user_data.channel_id
        )

        channel_members = db.session.query(UsersByChannelsTableEntry).filter(
            UsersByChannelsTableEntry.channel_id == user_data.channel_id
        )

        channel = db.session.query(ChannelTableEntry).filter(
            ChannelTableEntry.channel_id == user_data.channel_id
        ).one_or_none()

        try:
            messages = channel_messages.delete()
            db.session.flush()
            chats = channel_chats.delete()
            db.session.flush()
            members = channel_members.delete()
            db.session.flush()
            db.session.delete(channel)
            db.session.commit()
            cls.logger().info(
                f"Channel #{channel.channel_id} deleted by user {user.username}. {chats} chats deleted, "
                f"{messages} messages removed and {members} users-chats relations released.")
            return SuccessfulChannelMessageResponse("Channel removed!", ChannelResponseStatus.REMOVED.value)
        except exc.IntegrityError:
            db.session.rollback()
            cls.logger().error(f"User #{user.user_id} couldn't remove channel #{user_data.channel_id}.")
            return UnsuccessfulChannelMessageResponse("Couldn't remove channel.")
