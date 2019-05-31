from models.request import ClientRequest
from services.messages import MessageService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("MessagesController")


@app.route('/teams/<team_id>/messages/previews', methods=['GET'])
def get_preview_messages(team_id):
    logger.info(f"Attempting to get all preview messages for user from team #{team_id}.")
    req = ClientRequest(request)
    messages = MessageService.get_preview_messages(req.team_authentication(team_id))
    return jsonify(messages.json()), messages.status_code()


@app.route('/teams/<team_id>/messages/<chat_id>', methods=['GET'])
def get_messages_from_direct_chat(team_id, chat_id):
    logger.info(f"Attempting to get all messages from specific chat from user in team #{team_id}.")
    req = ClientRequest(request)
    messages = MessageService.get_messages_from_direct_chat(req.chat_data(team_id, chat_id))
    return jsonify(messages.json()), messages.status_code()


@app.route('/teams/messages', methods=['POST'])
def send_direct_message():
    logger.info(f"Attempting to send message in team.")
    req = ClientRequest(request)
    response = MessageService.send_direct_message(req.inbox_data())
    return jsonify(response.json()), response.status_code()
