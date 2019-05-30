from models.request import ClientRequest
from services.channels import ChannelService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("ChannelsController")


@app.route('/teams/<team_id>/channels', methods=['POST'])
def register_channel(team_id):
    logger.info(f"Attempting to register new channel in team #{team_id}")
    req = ClientRequest(request)
    new_channel = ChannelService.create_channel(req.new_channel_data(team_id))
    return jsonify(new_channel.json()), new_channel.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>/invite', methods=['POST'])
def add_member(team_id, channel_id):
    logger.info(f"Attempting to add new member to channel #{channel_id}")
    req = ClientRequest(request)
    new_member = ChannelService.add_member(req.channel_invitation_data(team_id, channel_id))
    return jsonify(new_member.json()), new_member.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>/join', methods=['POST'])
def join_channel(team_id, channel_id):
    logger.info(f"Attempting to join channel #{channel_id}")
    req = ClientRequest(request)
    new_member = ChannelService.join_channel(req.channel_registration_data(team_id, channel_id))
    return jsonify(new_member.json()), new_member.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>/leave', methods=['DELETE'])
def leave_channel(team_id, channel_id):
    logger.info(f"Attempting to leave channel #{channel_id}")
    req = ClientRequest(request)
    old_member = ChannelService.leave_channel(req.leave_channel_data(team_id, channel_id))
    return jsonify(old_member.json()), old_member.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>', methods=['DELETE'])
def delete_channel(team_id, channel_id):
    logger.info(f"Attempting to delete channel #{channel_id} from team #{team_id}")
    req = ClientRequest(request)
    old_channel = ChannelService.delete_channel(req.delete_channel_data(team_id, channel_id))
    return jsonify(old_channel.json()), old_channel.status_code()
