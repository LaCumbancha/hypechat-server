from tables.bots import BotTableEntry
from dtos.models.bots import Bot


class BotDatabaseMapper:

    @classmethod
    def to_bot(cls, bot):
        return BotTableEntry(
            bot_id=bot.id,
            team_id=bot.team_id,
            bot_name=bot.name,
            callback_url=bot.callback,
            token=bot.token
        )


class BotModelMapper:

    @classmethod
    def to_bot(cls, bot_entry):
        return Bot(
            bot_id=bot_entry.bot_id,
            name=bot_entry.bot_name,
            callback=bot_entry.callback_url,
            token=bot_entry.token
        ) if bot_entry is not None else None

    @classmethod
    def to_bots(cls, bots_entries):
        bots = []
        for bot_entry in bots_entries:
            bots += [Bot(
                bot_id=bot_entry.bot_id,
                name=bot_entry.bot_name,
                callback=bot_entry.callback_url,
                token=bot_entry.token
            )]
        return bots
