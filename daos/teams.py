from app import db
from sqlalchemy import and_, or_, literal

from daos.builder import TableEntryBuilder, ModelBuilder
from tables.users import *
from tables.teams import *
from dtos.models.teams import *


class TeamDatabaseClient:

    @classmethod
    def get_team_by_id(cls, team_id):
        team_entry = db.session.query(TeamTableEntry).filter(TeamTableEntry.team_id == team_id).one_or_none()
        return ModelBuilder.to_team(team_entry)

    @classmethod
    def get_user_teams_by_user_id(cls, user_id, is_admin=False):
        if is_admin:
            team_entry = db.session.query(
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                literal(None).label("role")
            ).all()
        else:
            team_entry = db.session.query(
                TeamTableEntry.team_id,
                TeamTableEntry.team_name,
                TeamTableEntry.picture,
                TeamTableEntry.location,
                TeamTableEntry.description,
                TeamTableEntry.welcome_message,
                UsersByTeamsTableEntry.role
            ).join(
                UsersByTeamsTableEntry,
                and_(
                    UsersByTeamsTableEntry.user_id == user_id,
                    UsersByTeamsTableEntry.team_id == TeamTableEntry.team_id
                )
            ).all()
        return ModelBuilder.to_teams(team_entry)
