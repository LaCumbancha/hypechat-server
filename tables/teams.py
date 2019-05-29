from app import db
from sqlalchemy import exc, ForeignKey
from tables.users import TeamTableEntry


class TeamsInvitesTableEntry(db.Model):
    __tablename__ = 'teams_invites'

    team_id = db.Column(ForeignKey(TeamTableEntry.team_id), name='team_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    email = db.Column(name='email', type_=db.String(), nullable=False, primary_key=True)
    invite_token = db.Column(name='invite_token', type_=db.String(), nullable=True, default=None)
