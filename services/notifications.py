from app import db
from tables.users import UserTableEntry
from tables.messages import MentionsByMessagesTableEntry
from sqlalchemy import exc, and_

import logging


class NotificationService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def notify_team_invitation(cls, invitation, inviter_id):
        pass

    @classmethod
    def notify_change_role(cls, user_team, admin_id):
        pass

    @classmethod
    def notify_channel_invitation(cls, user_channel, inviter_id):
        pass

    @classmethod
    def notify_message(cls, message):
        pass

    @classmethod
    def notify_mention(cls, message, mentioned_id):
        pass
