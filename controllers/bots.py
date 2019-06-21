from models.request import ClientRequest
from services.bots import BotService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("BotsController")


@app.route('/teams/bots', methods=['POST'])
def register_bot():
    logger.info(f"Attempting to register new bot in team.")
    req = ClientRequest(request)
    response = BotService.create_bot(req.new_bot_data())
    return jsonify(response.json()), response.status_code()
