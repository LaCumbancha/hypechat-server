from app import db

from daos.database import DatabaseClient
from daos.mappers.bots import BotDatabaseMapper, BotModelMapper

from tables.bots import BotTableEntry
from tables.users import UsersByTeamsTableEntry

from sqlalchemy import func


class BotDatabaseClient:

    @classmethod
    def add_bot(cls, bot):
        bot_entry = BotDatabaseMapper.to_bot(bot)
        DatabaseClient.add(bot_entry)

    @classmethod
    def get_bot_by_id(cls, bot_id):
        bot_entry = db.session.query(BotTableEntry).filter(BotTableEntry.bot_id == bot_id).one_or_none()
        return BotModelMapper.to_bot(bot_entry)

    @classmethod
    def get_bot_by_name(cls, name):
        bot_entry = db.session.query(BotTableEntry).filter(
            func.lower(BotTableEntry.bot_name) == name.lower()
        ).one_or_none()
        return BotModelMapper.to_bot(bot_entry)

    @classmethod
    def get_team_bots(cls, team_id):
        bots_entries = db.session.query(
            BotTableEntry.bot_id,
            BotTableEntry.bot_name,
            BotTableEntry.callback_url,
            BotTableEntry.token,
            UsersByTeamsTableEntry.team_id
        ).join(
            UsersByTeamsTableEntry,
            UsersByTeamsTableEntry.user_id == BotTableEntry.bot_id
        ).filter(
            UsersByTeamsTableEntry.team_id == team_id
        ).all()
        return BotModelMapper.to_bots(bots_entries)
