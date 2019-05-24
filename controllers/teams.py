from models.constants import StatusCode
from models.request import ClientRequest
from services.teams import TeamService

from flask import request, jsonify
from run import app

import logging
logger = logging.getLogger("TeamsController")


@app.route('/teams', methods=['POST'])
def register_team():
    logger.info("Attempting to register new team")
    req = ClientRequest(request)
    new_team = TeamService.create_team(req.new_team_data())
    return jsonify(new_team.json()), new_team.status_code()


@app.route('/teams/register-user', methods=['POST'])
def register_user_team():
    logger.info("Attempting to register new user in team")
    req = ClientRequest(request)
    new_user_team = TeamService.register_user_team(req.new_user_team_data())
    return jsonify(new_user_team.json()), new_user_team.status_code()
