from app import db
from dtos.responses.channels import *
from models.authentication import Authenticator
from tables.users import UsersByChannelsTableEntry, UsersByTeamsTableEntry, UserTableEntry
from tables.channels import *
from sqlalchemy import exc

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
                return BadRequestChannelMessageResponse(f"Channel {creation_data.name} already in use for other channel.",
                                                        TeamResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().error(f"Failing to create channel {creation_data.name}.")
                return UnsuccessfulChannelMessageResponse("Couldn't create channel.")
        else:
            return SuccessfulChannelResponse(new_channel, TeamResponseStatus.CREATED.value)

    @classmethod
    def add_member(cls, invitation_data):
        user = Authenticator.authenticate_channel(invitation_data.authentication,
                                                  lambda user, creator: TeamRoles.is_channel_creator(user, creator))

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
                return UnsuccessfulChannelMessageResponse("Couldn't add channel.")
        else:
            return SuccessfulChannelMessageResponse("User added!", TeamResponseStatus.ADDED.value)

    @classmethod
    def join_channel(cls, registration_data):
        pass

    @classmethod
    def leave_channel(cls, user_data):
        pass

    @classmethod
    def delete_channel(cls, user_data):
        pass
