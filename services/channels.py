from app import db
from dtos.responses.channels import *
from models.authentication import Authenticator
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
        pass

    @classmethod
    def join_channel(cls, registration_data):
        pass

    @classmethod
    def leave_channel(cls, user_data):
        pass

    @classmethod
    def delete_channel(cls, user_data):
        pass
