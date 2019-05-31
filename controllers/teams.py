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


@app.route('/teams/invite', methods=['POST'])
def invite_user():
    logger.info(f"Attempting to invite new user to team.")
    req = ClientRequest(request)
    new_invite = TeamService.invite_user(req.invite_data())
    return jsonify(new_invite.json()), new_invite.status_code()


@app.route('/teams/join', methods=['POST'])
def accept_invite():
    logger.info(f"Attempting to join team.")
    req = ClientRequest(request)
    new_user_team = TeamService.accept_invite(req.accept_invite())
    return jsonify(new_user_team.json()), new_user_team.status_code()


@app.route('/teams/<team_id>/users/<searched_username>', methods=['GET'])
def search_user(team_id, searched_username):
    logger.info(f"Attempting to search for user in team {team_id}")
    req = ClientRequest(request)
    found_users = TeamService.search_users(req.search_users_data(team_id, searched_username))
    return jsonify(found_users.json()), found_users.status_code()


@app.route('/teams/<team_id>/roles', methods=['PATCH'])
def change_role(team_id):
    logger.info(f"Attempting to change roles in team {team_id}.")
    req = ClientRequest(request)
    roles_changed = TeamService.change_role(req.change_role(team_id))
    return jsonify(roles_changed.json()), roles_changed.status_code()


@app.route('/teams/<team_id>/users', methods=['GET'])
def team_users(team_id):
    logger.info(f"Attempting to get all users from team {team_id}.")
    req = ClientRequest(request)
    users = TeamService.team_users(req.team_authentication(team_id))
    return jsonify(users.json()), users.status_code()


@app.route('/teams/<team_id>/users/<user_id>/profile', methods=['GET'])
def team_user_profile(team_id, user_id):
    logger.info(f"Attempting to get user {user_id} from team {team_id} profile.")
    req = ClientRequest(request)
    users = TeamService.team_user_by_id(req.search_user_by_id(team_id, user_id))
    return jsonify(users.json()), users.status_code()


@app.route('/teams/<team_id>/users/<delete_id>', methods=['DELETE'])
def delete_users(team_id, delete_id):
    logger.info(f"Attempting to delete user {delete_id} from team {team_id}.")
    req = ClientRequest(request)
    response = TeamService.delete_users(req.delete_user_data(team_id, delete_id))
    return jsonify(response.json()), response.status_code()


@app.route('/teams/<team_id>/leave', methods=['DELETE'])
def leave_team(team_id):
    logger.info(f"Attempting to leave team {team_id}.")
    req = ClientRequest(request)
    response = TeamService.leave_team(req.team_authentication(team_id))
    return jsonify(response.json()), response.status_code()


@app.route('/teams/<team_id>', methods=['DELETE'])
def delete_team(team_id):
    logger.info(f"Attempting to delete team {team_id}.")
    req = ClientRequest(request)
    response = TeamService.delete_team(req.team_authentication(team_id))
    return jsonify(response.json()), response.status_code()


@app.route('/teams/<team_id>', methods=['PATCH'])
def update_team_information(team_id):
    logger.info(f"Attempting to update team {team_id} information.")
    req = ClientRequest(request)
    team_updated = TeamService.update_information(req.team_update(team_id))
    return jsonify(team_updated.json()), team_updated.status_code()
