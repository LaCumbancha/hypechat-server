from models.request import ClientRequest
from services.channels import ChannelService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("ChannelsController")


@app.route('/teams/channels', methods=['POST'])
def register_channel():
    logger.info(f"Attempting to register new channel in team.")
    req = ClientRequest(request)
    new_channel = ChannelService.create_channel(req.new_channel_data())
    return jsonify(new_channel.json()), new_channel.status_code()


@app.route('/teams/channels/users', methods=['POST'])
def add_member():
    logger.info(f"Attempting to add new member to team channel.")
    req = ClientRequest(request)
    new_member = ChannelService.add_member(req.channel_invitation_data())
    return jsonify(new_member.json()), new_member.status_code()


@app.route('/teams/channels/join', methods=['POST'])
def join_channel():
    logger.info(f"Attempting to join team channel.")
    req = ClientRequest(request)
    new_member = ChannelService.join_channel(req.channel_registration_data())
    return jsonify(new_member.json()), new_member.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>/users/<user_id>', methods=['DELETE'])
def remove_member(team_id, channel_id, user_id):
    logger.info(f"Attempting to remove member #{user_id} from team #{team_id}'s channel #{channel_id}.")
    req = ClientRequest(request)
    new_member = ChannelService.remove_member(req.delete_user_channel_data(team_id, channel_id, user_id))
    return jsonify(new_member.json()), new_member.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>/users', methods=['GET'])
def channel_members(team_id, channel_id):
    logger.info(f"Attempting to get members from team #{team_id}'s channel #{channel_id}.")
    req = ClientRequest(request)
    new_member = ChannelService.channel_members(req.channel_authentication_data(team_id, channel_id))
    return jsonify(new_member.json()), new_member.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>/leave', methods=['DELETE'])
def leave_channel(team_id, channel_id):
    logger.info(f"Attempting to leave channel #{channel_id}")
    req = ClientRequest(request)
    old_member = ChannelService.leave_channel(req.channel_authentication_data(team_id, channel_id))
    return jsonify(old_member.json()), old_member.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>', methods=['DELETE'])
def delete_channel(team_id, channel_id):
    logger.info(f"Attempting to delete channel #{channel_id} from team #{team_id}")
    req = ClientRequest(request)
    old_channel = ChannelService.delete_channel(req.channel_authentication_data(team_id, channel_id))
    return jsonify(old_channel.json()), old_channel.status_code()


@app.route('/teams/<team_id>/channels/<channel_id>', methods=['PATCH'])
def update_channel_information(team_id, channel_id):
    logger.info(f"Attempting to update channel #{channel_id} information from team #{team_id}")
    req = ClientRequest(request)
    updated_channel = ChannelService.update_information(req.channel_update_data(team_id, channel_id))
    return jsonify(updated_channel.json()), updated_channel.status_code()
