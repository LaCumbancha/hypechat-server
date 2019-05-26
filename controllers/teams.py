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


@app.route('/teams/<team_id>/invite', methods=['POST'])
def invite_user(team_id):
    logger.info("Attempting to invite new user into team.")
    req = ClientRequest(request)
    new_user_team = TeamService.invite_user(req.invite_data(team_id))
    return jsonify(new_user_team.json()), new_user_team.status_code()


@app.route('/teams/<team_id>/join', methods=['POST'])
def accept_invite(team_id):
    logger.info("Attempting to join team.")
    req = ClientRequest(request)
    new_user_team = TeamService.accept_invite(req.accept_invite(team_id))
    return jsonify(new_user_team.json()), new_user_team.status_code()
