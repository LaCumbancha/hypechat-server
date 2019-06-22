from utils.serializer import Jsonizable
from utils.responses import Response

from models.constants import StatusCode, UserResponseStatus


class SuccessfulBotListResponse(Jsonizable, Response):

    def __init__(self, bots):
        self.bots = bots

    def json(self):
        return {
            "status": UserResponseStatus.LIST.value,
            "bots": self._output_bot()
        }

    def _output_bot(self):
        return list(map(lambda bot: {
            "id": bot.id,
            "name": bot.name
        }, self.bots))

    def status_code(self):
        return StatusCode.OK.value
