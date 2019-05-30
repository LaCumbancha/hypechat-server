from app import db
from sqlalchemy import exc, ForeignKey


class TeamTableEntry(db.Model):
    __tablename__ = 'teams'

    team_id = db.Column(name='id', type_=db.Integer, nullable=False, primary_key=True, autoincrement=True)
    team_name = db.Column(name='name', type_=db.String(), nullable=False, unique=True)
    picture = db.Column(name='picture', type_=db.String(), nullable=True)
    location = db.Column(name='location', type_=db.String(), nullable=True)
    description = db.Column(name='description', type_=db.String(), nullable=True)
    welcome_message = db.Column(name='welcome_message', type_=db.String(), nullable=True)


class TeamsInvitesTableEntry(db.Model):
    __tablename__ = 'teams_invites'

    team_id = db.Column(ForeignKey(TeamTableEntry.team_id), name='team_id', type_=db.Integer,
                        nullable=False, primary_key=True)
    email = db.Column(name='email', type_=db.String(), nullable=False, primary_key=True)
    invite_token = db.Column(name='invite_token', type_=db.String(), nullable=True, default=None)
