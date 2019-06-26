from pyfcm import FCMNotification

from daos.bots import BotDatabaseClient
from daos.users import UserDatabaseClient
from daos.teams import TeamDatabaseClient
from daos.channels import ChannelDatabaseClient

from models.constants import TeamRoles, NotificationType

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
        team = TeamDatabaseClient.get_team_by_id(invitation.team_id)

        if invited_user is not None:
            message_body = "You have been invited to join a team!"
            data = {
                "notification_type": NotificationType.TEAM_INVITATION.value,
                "team_name": team.name,
                "inviter": {
                    "id": inviter_user.id,
                    "username": inviter_user.username,
                    "first_name": inviter_user.first_name,
                    "last_name": inviter_user.last_name
                },
                "invitation_token": invitation.token
            }

            try:
                cls.logger().debug(f"Sending notification to topic {invited_user.id}, with title \"{cls.APP_NAME}\" "
                                   f"and body \"{message_body}\"")
                response = cls.push_service.notify_topic_subscribers(topic_name=invited_user.id,
                                                                     message_title=cls.APP_NAME,
                                                                     message_body=message_body, data_message=data)

                failures = response.get("failure")
                if failures > 0:
                    cls.logger().error(f"There's been detected {failures} failures sending user #{invited_user.id}'s "
                                       f"team invite notification to Firebase.")
                else:
                    cls.logger().info(f"Team invite notified to user #{invited_user.id}.")

            except ConnectionError:
                cls.logger().error("Couldn't connect to Firebase server.")

        else:
            cls.logger().info(f"The invited user is not already registered so it cannot receive a notification.")

    @classmethod
    def notify_change_role(cls, user_team, old_role, admin_id):
        admin = UserDatabaseClient.get_user_by_id(admin_id)
        team = TeamDatabaseClient.get_team_by_id(user_team.team_id)
        new_role = user_team.role

        condition = "upgraded" if TeamRoles.is_higher_role(new_role, old_role) else "downgraded"
        message_body = f"You have been {condition} in team {team.name}!"
        data = {
            "notification_type": NotificationType.TEAM_ROLE_CHANGE.value,
            "team_name": team.name,
            "admin": {
                "id": admin.id,
                "username": admin.username,
                "first_name": admin.first_name,
                "last_name": admin.last_name
            }
        }

        try:
            cls.logger().debug(f"Sending notification to topic {user_team.user_id}, with title \"{cls.APP_NAME}\" "
                               f"and body \"{message_body}\"")
            response = cls.push_service.notify_topic_subscribers(topic_name=user_team.user_id,
                                                                 message_title=cls.APP_NAME,
                                                                 message_body=message_body, data_message=data)

            failures = response.get("failure")
            if failures > 0:
                cls.logger().error(f"There's been detected {failures} failures sending user #{user_team.user_id} new "
                                   f"role notifications to Firebase.")
            else:
                cls.logger().info(f"New role notified to user #{user_team.user_id}.")

        except ConnectionError:
            cls.logger().error("Couldn't connect to Firebase server.")

    @classmethod
    def notify_channel_invitation(cls, user_channel, inviter_id):
        inviter_user = UserDatabaseClient.get_user_by_id(inviter_id)
        channel = ChannelDatabaseClient.get_channel_by_id(user_channel.channel_id)
        team = TeamDatabaseClient.get_team_by_id(channel.team_id)

        message_body = f"You have been added to channel {channel.name} in team {team.name}!"
        data = {
            "notification_type": NotificationType.CHANNEL_INVITATION.value,
            "channel_name": channel.name,
            "team_name": team.name,
            "inviter": {
                "id": inviter_user.id,
                "username": inviter_user.username,
                "first_name": inviter_user.first_name,
                "last_name": inviter_user.last_name
            }
        }

        try:
            cls.logger().debug(f"Sending notification to topic {user_channel.user_id}, with title \"{cls.APP_NAME}\" "
                               f"and body \"{message_body}\"")
            response = cls.push_service.notify_topic_subscribers(topic_name=user_channel.user_id,
                                                                 message_title=cls.APP_NAME,
                                                                 message_body=message_body, data_message=data)

            failures = response.get("failure")
            if failures > 0:
                cls.logger().error(f"There's been detected {failures} failures sending user #{user_channel.user_id}'s "
                                   f"channel invite notification to Firebase.")
            else:
                cls.logger().info(f"Channel invitation notified to user #{user_channel.user_id}.")

        except ConnectionError:
            cls.logger().error("Couldn't connect to Firebase server.")

    @classmethod
    def notify_message(cls, message, is_user_receiver):
        team = TeamDatabaseClient.get_team_by_id(message.team_id)
        sender = UserDatabaseClient.get_user_by_id(message.sender_id)

        if sender is None:
            sender = BotDatabaseClient.get_bot_by_id(message.sender_id)
            sender_data = {
                "id": sender.id,
                "name": sender.name
            }
        else:
            sender_data = {
                "id": sender.id,
                "username": sender.username,
                "first_name": sender.first_name,
                "last_name": sender.last_name
            }

        message_body = "You receive a direct message!"
        data = {
            "notification_type": NotificationType.MESSAGE.value,
            "team_name": team.name,
            "sender": sender_data
        }

        if not is_user_receiver:
            channel = ChannelDatabaseClient.get_channel_by_id(message.receiver_id)
            message_body = "Your receive a channel message!"
            data["channel_name"] = channel.name

        try:
            cls.logger().debug(f"Sending notification to topic {message.receiver_id}, with title \"{cls.APP_NAME}\" "
                               f"and body \"{message_body}\"")
            response = cls.push_service.notify_topic_subscribers(topic_name=message.receiver_id,
                                                                 message_title=cls.APP_NAME,
                                                                 message_body=message_body, data_message=data)

            failures = response.get("failure")
            if failures > 0:
                cls.logger().error(f"There's been detected {failures} failures sending the messages notification for "
                                   f"receiver #{message.receiver_id} to Firebase.")
            else:
                cls.logger().info(f"New message notified to receiver #{message.receiver_id}.")

        except ConnectionError:
            cls.logger().error("Couldn't connect to Firebase server.")

    @classmethod
    def notify_mention(cls, message, mentioned_id):
        is_not_bot = BotDatabaseClient.get_bot_by_id(mentioned_id) is None

        if is_not_bot:
            sender_user = UserDatabaseClient.get_user_by_id(message.sender_id)
            team = TeamDatabaseClient.get_team_by_id(message.team_id)

            message_body = "You have been mentioned!"
            data = {
                "notification_type": NotificationType.MENTION.value,
                "team_name": team.name,
                "sender": {
                    "sender": sender_user.id,
                    "username": sender_user.username,
                    "first_name": sender_user.first_name,
                    "last_name": sender_user.last_name
                }
            }

            channel = ChannelDatabaseClient.get_channel_by_id(mentioned_id)
            if channel is not None:
                data["channel_name"] = channel.name

            try:
                cls.logger().debug(f"Sending notification to topic {mentioned_id}, with title \"{cls.APP_NAME}\" "
                                   f"and body \"{message_body}\"")
                response = cls.push_service.notify_topic_subscribers(topic_name=mentioned_id,
                                                                     message_title=cls.APP_NAME,
                                                                     message_body=message_body, data_message=data)

                failures = response.get("failure")
                if failures > 0:
                    cls.logger().error(
                        f"There's been detected {failures} failures sending the mentions notification for "
                        f"receiver #{message.receiver_id} to Firebase.")
                else:
                    cls.logger().info(f"New mention notified to receiver #{message.receiver_id}.")
            except ConnectionError:
                cls.logger().error("Couldn't connect to Firebase server.")
