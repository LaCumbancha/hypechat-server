from tables.bots import BotTableEntry
from dtos.models.bots import Bot


class BotDatabaseMapper:

    @classmethod
    def to_bot(cls, bot):
        return BotTableEntry(
            bot_id=bot.id,
            bot_name=bot.name,
            callback_url=bot.callback
        )


class BotModelMapper:

    @classmethod
    def to_bot(cls, bot_entry):
        return Bot(
            bot_id=bot_entry.bot_id,
            name=bot_entry.bot_name,
            callback=bot_entry.callback_url
        )
