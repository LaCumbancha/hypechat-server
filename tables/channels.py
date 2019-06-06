from app import db
from sqlalchemy import exc, ForeignKey
from tables.users import ClientTableEntry
from tables.teams import TeamTableEntry
from models.constants import ChannelVisibilities


class ChannelTableEntry(db.Model):
    __tablename__ = 'channels'

    channel_id = db.Column(ForeignKey(ClientTableEntry.client_id), name='id', type_=db.Integer,
                           nullable=False, primary_key=True)
    team_id = db.Column(name='team_id', type_=db.Integer, nullable=False)
    name = db.Column(name='name', type_=db.String(), nullable=False)
    creator = db.Column(name='creator', type_=db.String(), nullable=False)
    visibility = db.Column(name='visibility', type_=db.String(), nullable=False,
                           server_default=ChannelVisibilities.PUBLIC.value)
    description = db.Column(name='description', type_=db.String(), nullable=True)
    welcome_message = db.Column(name='welcome_message', type_=db.String(), nullable=True)
