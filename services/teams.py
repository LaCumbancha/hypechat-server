from app import db
from dtos.responses.clients import *
from models.authentication import Authenticator
from tables.users import *
from models.constants import TeamRoles
from sqlalchemy import exc

import logging


class TeamService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_team(cls, new_team_data):
        user = Authenticator.authenticate(new_team_data)
        new_team = TeamTableEntry(
            team_name=new_team_data.team_name,
            location=new_team_data.location,
            description=new_team_data.description,
            welcome_message=new_team_data.welcome_message
        )

        try:
            db.session.add(new_team)
            db.session.flush()
            new_user_by_team = UsersByTeamsTableEntry(
                user_id=user.user_id,
                team_id=new_team.team_id,
                role=TeamRoles.CREATOR.value
            )
            db.session.add(new_user_by_team)
            db.session.flush()
            db.session.commit()
            cls.logger().info(f"Team #{new_team.team_id} created.")
            cls.logger().info(
                f"User #{user.user_id} assigned as team #{new_team.team_id} ({new_team.team_name}) #{new_user_by_team.role}.")
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(TeamTableEntry).filter(TeamTableEntry.team_name == new_team_data.team_name).first():
                cls.logger().info(
                    f"Failing to create team {new_team_data.team_name}. Name already in use for other team.")
                return ClientAlreadyCreatedResponse(f"Name {new_team_data.team_name} already in use for other team.")
            else:
                cls.logger().info(f"Failing to create team {new_team_data.team_name}.")
                return UnsuccessfulClientResponse("Couldn't create team.")
        else:
            return SuccessfulTeamResponse(new_team)
