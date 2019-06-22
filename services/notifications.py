from app import db
from pyfcm import FCMNotification

from daos.users import UserDatabaseClient
from daos.teams import TeamDatabaseClient
from daos.channels import ChannelDatabaseClient

from models.constants import TeamRoles

import logging
import os


class NotificationService:
    FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
    APP_NAME = "Hypechat"
    push_service = FCMNotification(api_key=FIREBASE_API_KEY)

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def notify_team_invitation(cls, invitation, inviter_id):
        inviter_user = UserDatabaseClient.get_user_by_id(inviter_id)
        invited_user = UserDatabaseClient.get_user_by_email(invitation.email)

        if invited_user is not None:
            message_body = "You have been invited to join a team!"
            data = {
                "team_name": invitation.team_name,
                "inviter": {
                    "username": inviter_id.username,
                    "first_name": invited_user.first_name,
                    "last_name": inviter_user.last_name
                },
                "invitation_token": invitation.token
            }
            response = cls.push_service.notify_topic_subscribers(topic_name=invited_user.id, message_title=cls.APP_NAME,
                                                                 message_body=message_body, data_message=data)

            if response.get("failure"):
                cls.logger().error(f"There's been some problems sending user #{invited_user.id}'s team invite "
                                   f"notification.")
            else:
                cls.logger().info(f"User #{invited_user.id}'s team invitation notified.")

    @classmethod
    def notify_change_role(cls, user_team, old_role, admin_id):
        admin = UserDatabaseClient.get_user_by_id(admin_id)
        team = TeamDatabaseClient.get_team_by_id(user_team.team_id)
        new_role = user_team.role

        condition = "upgraded" if TeamRoles.is_higher_role(new_role, old_role) else "downgraded"
        message_body = f"You have been {condition} in team {team.name}!"
        data = {
            "team_name": team.name,
            "admin": {
                "username": admin.username,
                "first_name": admin.first_name,
                "last_name": admin.last_name
            }
        }
        response = cls.push_service.notify_topic_subscribers(topic_name=user_team.user_id, message_title=cls.APP_NAME,
                                                             message_body=message_body, data_message=data)

        if response.get("failure"):
            cls.logger().error(f"There's been some problems sending user #{user_team.user_id} new role notifications")
        else:
            cls.logger().info(f"User #{user_team.user_id}'s new role notified.")

    @classmethod
    def notify_channel_invitation(cls, user_channel, inviter_id):
        inviter_user = UserDatabaseClient.get_user_by_id(inviter_id)
        channel = ChannelDatabaseClient.get_channel_by_id(user_channel.channel_id)
        team = TeamDatabaseClient.get_team_by_id(channel.team_id)

        message_body = f"You have been added to channel {channel.name} in team {team.name}!"
        data = {
            "channel_name": channel.name,
            "team_name": team.name,
            "inviter": {
                "username": inviter_user.username,
                "first_name": inviter_user.first_name,
                "last_name": inviter_user.last_name
            }
        }
        response = cls.push_service.notify_topic_subscribers(topic_name=user_channel.user_id, message_title=cls.APP_NAME,
                                                             message_body=message_body, data_message=data)

        if response.get("failure"):
            cls.logger().error(f"There's been some problems sending user #{inviter_user.id}'s' channel invite "
                               f"notification.")
        else:
            cls.logger().info(f"User #{invited_user.id}'s channel invitation notified.")

    @classmethod
    def notify_message(cls, message, is_user_receiver):
        sender_user = UserDatabaseClient.get_user_by_id(message.sender_id)
        team = TeamDatabaseClient.get_team_by_id(message.team_id)

        message_body = "You receive a direct message!"
        data = {
            "team_name": team.name,
            "sender": {
                "username": sender_user.username,
                "first_name": sender_user.first_name,
                "last_name": sender_user.last_name
            }
        }

        if not is_user_receiver:
            channel = ChannelDatabaseClient.get_channel_by_id(message.receiver_id)
            message_body = "Your receive a channel message!"
            data["channel_name"] = channel.name

        response = cls.push_service.notify_topic_subscribers(topic_name=message.receiver_id, message_title=cls.APP_NAME,
                                                             message_body=message_body, data_message=data)

        if response.get("failure"):
            cls.logger().error(f"There's been some problems sending the messages notification for receiver "
                               f"#{message.receiver_id}.")
        else:
            cls.logger().info(f"Receiver #{message.receiver_id}'s messages notified.")

    @classmethod
    def notify_mention(cls, message, mentioned_id):
        sender_user = UserDatabaseClient.get_user_by_id(message.sender_id)
        team = TeamDatabaseClient.get_team_by_id(message.team_id)

        message_body = "You have been mentioned!"
        data = {
            "team_name": team.name,
            "sender": {
                "username": sender_user.username,
                "first_name": sender_user.first_name,
                "last_name": sender_user.last_name
            }
        }

        channel = ChannelDatabaseClient.get_channel_by_id(mentioned_id)
        if channel is not None:
            data["channel_name"] = channel.name

        response = cls.push_service.notify_topic_subscribers(topic_name=mentioned_id, message_title=cls.APP_NAME,
                                                             message_body=message_body, data_message=data)

        if response.get("failure"):
            cls.logger().error(f"There's been some problems sending the mentions notification for receiver "
                               f"#{message.receiver_id}.")
        else:
            cls.logger().info(f"Receiver #{message.receiver_id}'s mentions notified.")
