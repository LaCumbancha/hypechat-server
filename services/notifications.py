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
    APP_NAME = "HYPECHAT"
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
                cls.logger().error("There's been some problems sending the invite notification.")
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
        response = cls.push_service.notify_topic_subscribers(topic_name=invited_user.id, message_title=cls.APP_NAME,
                                                             message_body=message_body, data_message=data)

        if response.get("failure"):
            cls.logger().error("There's been some problems sending the new role notifications")
        else:
            cls.logger().info(f"User #{user_team.user_id}'s new role notified.")

    @classmethod
    def notify_channel_invitation(cls, user_channel, inviter_id):
        data = {}
        pass

    @classmethod
    def notify_message(cls, message):
        data = {}
        pass

    @classmethod
    def notify_mention(cls, message, mentioned_id):
        data = {}
        pass
