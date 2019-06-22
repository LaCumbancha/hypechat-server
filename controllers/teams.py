from models.constants import StatusCode
from models.request import ClientRequest
from services.teams import TeamService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("TeamsController")


@app.route('/teams', methods=['POST'])
def register_team():
    logger.info("Attempting to register new team.")
    req = ClientRequest(request)
    new_team = TeamService.create_team(req.new_team_data())
    return jsonify(new_team.json()), new_team.status_code()


@app.route('/teams/users', methods=['POST'])
def add_user():
    logger.info(f"Attempting to add user to team.")
    req = ClientRequest(request)
    user_added = TeamService.add_user(req.add_user_team_data())
    return jsonify(user_added.json()), user_added.status_code()


@app.route('/teams/invite', methods=['POST'])
def invite_user():
    logger.info(f"Attempting to invite new user to team.")
    req = ClientRequest(request)
    new_invite = TeamService.invite_user(req.team_invite_data())
    return jsonify(new_invite.json()), new_invite.status_code()


@app.route('/teams/join', methods=['POST'])
def accept_invite():
    logger.info(f"Attempting to join team.")
    req = ClientRequest(request)
    new_user_team = TeamService.accept_invite(req.accept_team_invite_data())
    return jsonify(new_user_team.json()), new_user_team.status_code()


@app.route('/teams/<team_id>/users/<searched_username>', methods=['GET'])
def search_user(team_id, searched_username):
    logger.info(f"Attempting to search for user in team #{team_id}")
    req = ClientRequest(request)
    found_users = TeamService.search_users(req.search_users_by_username_data(team_id, searched_username))
    return jsonify(found_users.json()), found_users.status_code()


@app.route('/teams/<team_id>/roles', methods=['PATCH'])
def change_role(team_id):
    logger.info(f"Attempting to change roles in team #{team_id}.")
    req = ClientRequest(request)
    roles_changed = TeamService.change_role(req.change_role_data(team_id))
    return jsonify(roles_changed.json()), roles_changed.status_code()


@app.route('/teams/forbidden-words', methods=['PUT'])
def add_forbidden_word():
    logger.info(f"Attempting to add a forbidden word to team.")
    req = ClientRequest(request)
    response = TeamService.add_forbidden_word(req.add_forbidden_word_data())
    return jsonify(response.json()), response.status_code()


@app.route('/teams/<team_id>/forbidden-words', methods=['GET'])
def forbidden_words(team_id):
    logger.info(f"Attempting to get forbidden words from team {team_id}.")
    req = ClientRequest(request)
    words = TeamService.forbidden_words(req.team_authentication_data(team_id))
    return jsonify(words.json()), words.status_code()


@app.route('/teams/<team_id>/forbidden-words/<word_id>', methods=['DELETE'])
def delete_forbidden_word(team_id, word_id):
    logger.info(f"Attempting to delete forbidden word #{word_id} from team #{team_id}.")
    req = ClientRequest(request)
    response = TeamService.delete_forbidden_word(req.delete_forbidden_word_data(team_id, word_id))
    return jsonify(response.json()), response.status_code()


@app.route('/teams/<team_id>/users', methods=['GET'])
def team_users(team_id):
    logger.info(f"Attempting to get all users from team #{team_id}.")
    req = ClientRequest(request)
    users = TeamService.team_users(req.team_authentication_data(team_id))
    return jsonify(users.json()), users.status_code()


@app.route('/teams/<team_id>/channels', methods=['GET'])
def team_channels(team_id):
    logger.info(f"Attempting to get all channels from team #{team_id}.")
    req = ClientRequest(request)
    channels = TeamService.team_channels(req.team_authentication_data(team_id))
    return jsonify(channels.json()), channels.status_code()


@app.route('/teams/<team_id>/users/<user_id>/profile', methods=['GET'])
def team_user_profile(team_id, user_id):
    logger.info(f"Attempting to get user {user_id} profile, from team #{team_id}.")
    req = ClientRequest(request)
    users = TeamService.team_user_profile(req.team_user_profile_data(team_id, user_id))
    return jsonify(users.json()), users.status_code()


@app.route('/teams/<team_id>/users/<delete_id>', methods=['DELETE'])
def delete_users(team_id, delete_id):
    logger.info(f"Attempting to delete user {delete_id} from team #{team_id}.")
    req = ClientRequest(request)
    response = TeamService.delete_users(req.delete_user_team_data(team_id, delete_id))
    return jsonify(response.json()), response.status_code()


@app.route('/teams/<team_id>/leave', methods=['DELETE'])
def leave_team(team_id):
    logger.info(f"Attempting to leave team #{team_id}.")
    req = ClientRequest(request)
    response = TeamService.leave_team(req.team_authentication_data(team_id))
    return jsonify(response.json()), response.status_code()


@app.route('/teams/<team_id>', methods=['DELETE'])
def delete_team(team_id):
    logger.info(f"Attempting to delete team #{team_id}.")
    req = ClientRequest(request)
    response = TeamService.delete_team(req.team_authentication_data(team_id))
    return jsonify(response.json()), response.status_code()


@app.route('/teams/<team_id>', methods=['PATCH'])
def update_team_information(team_id):
    logger.info(f"Attempting to update team #{team_id} information.")
    req = ClientRequest(request)
    updated_team = TeamService.update_information(req.team_update_data(team_id))
    return jsonify(updated_team.json()), updated_team.status_code()
