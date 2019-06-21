from models.request import ClientRequest

from services.users import UserService
from services.messages import MessageService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("StatsController")


@app.route('/stats/users', methods=['GET'])
def get_all_users():
    logger.info("Attempting to get users stats")
    req = ClientRequest(request)
    response = UserService.get_all_users(req.authentication_data())
    return jsonify(response.json()), response.status_code()


@app.route('/stats/messages', methods=['GET'])
def team_messages():
    logger.info(f"Attempting to get messages stats.")
    req = ClientRequest(request)
    stats = MessageService.messages_stats(req.authentication_data())
    return jsonify(stats.json()), stats.status_code()
