from app import db
from dtos.responses.clients import *
from dtos.responses.teams import *
from exceptions.exceptions import *
from models.authentication import Authenticator
from tables.users import *
from passlib.apps import custom_app_context as hashing
from sqlalchemy import exc, and_

import logging


class UserService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def create_user(cls, user_data):
        new_client = ClientTableEntry()

        try:
            db.session.add(new_client)
            db.session.flush()
            new_user = UserTableEntry(
                user_id=new_client.client_id,
                username=user_data.username,
                email=user_data.email,
                password=hashing.hash(user_data.password),
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                profile_pic=user_data.profile_pic,
                token=Authenticator.generate(user_data.username, user_data.password)
            )
            db.session.add(new_user)
            db.session.flush()
            db.session.commit()
            cls.logger().info(f"User #{new_client.client_id} created.")
        except exc.IntegrityError:
            db.session.rollback()
            if db.session.query(UserTableEntry).filter(UserTableEntry.email == user_data.email).one_or_none():
                cls.logger().info(
                    f"Failing to create user {new_client.client_id}. Email already in use for other user.")
                return BadRequestTeamResponse("Email already in use for other user.",
                                              UserResponseStatus.ALREADY_REGISTERED.value)
            elif db.session.query(UserTableEntry).filter(
                    UserTableEntry.username == user_data.username).one_or_none():
                cls.logger().info(
                    f"Failing to create user #{new_client.client_id}. Username already in use for other user.")
                return BadRequestTeamResponse("Username already in use for other user.",
                                              UserResponseStatus.ALREADY_REGISTERED.value)
            else:
                cls.logger().info(f"Failing to create user #{new_client.client_id}.")
                return UnsuccessfulClientResponse("Couldn't create user.")
        else:
            headers = {
                "username": new_user.username,
                "auth_token": new_user.auth_token
            }
            return SuccessfulUserResponse(new_user, headers)

    @classmethod
    def login_user(cls, user_data):
        user = db.session.query(UserTableEntry).filter(
            UserTableEntry.email == user_data.email).one_or_none()

        if user:
            if hashing.verify(user_data.password, user.password):
                user.auth_token = Authenticator.generate(user.username, user_data.password)
                user.online = True
                db.session.commit()
                cls.logger().info(f"Logging in user {user.user_id}")
                headers = {
                    "username": user.username,
                    "auth_token": user.auth_token
                }
                return SuccessfulUserResponse(user, headers)
            else:
                cls.logger().info(f"Wrong credentials while attempting to log in user #{user_data.email}")
                return WrongCredentialsResponse("Wrong email or password.")
        else:
            cls.logger().info(f"User #{user_data.email} not found.")
            raise UserNotFoundError("User not found.", UserResponseStatus.USER_NOT_FOUND.value)

    @classmethod
    def logout_user(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.auth_token = None
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} logged out.")
        return UserLoggedOutResponse("User logged out.")

    @classmethod
    def set_user_online(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.online = True
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} set online.")
        return SuccessfulUserResponse(user)

    @classmethod
    def set_user_offline(cls, user_data):
        user = Authenticator.authenticate(user_data)
        user.online = False
        db.session.commit()
        cls.logger().info(f"User #{user.user_id} set offline.")
        return SuccessfulUserResponse(user)

    @classmethod
    def search_users(cls, user_data):
        user = Authenticator.authenticate(user_data)

        found_users = db.session.query(UserTableEntry).filter(
            UserTableEntry.username.like(f"%{user_data.searched_username}%")).all()

        cls.logger().info(
            f"Found {len(found_users)} users for user #{user.user_id} with keyword {user.username} .")
        return SuccessfulUsersListResponse(cls._generate_users_list(found_users))

    @classmethod
    def _generate_users_list(cls, users_list):
        users = []

        for user in users_list:
            users += [{
                "id": user.user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile_pic": user.profile_pic,
                "online": user.online
            }]

        return users

    @classmethod
    def teams_for_user(cls, user_data):
        user = Authenticator.authenticate(user_data)

        teams = db.session.query(
            TeamTableEntry.team_id,
            TeamTableEntry.team_name,
            TeamTableEntry.location,
            TeamTableEntry.description,
            TeamTableEntry.welcome_message,
            UsersByTeamsTableEntry.role
        ).join(
            UsersByTeamsTableEntry,
            and_(
                UsersByTeamsTableEntry.user_id == user.user_id,
                UsersByTeamsTableEntry.team_id == TeamTableEntry.team_id
            )
        ).all()

        return SuccessfulTeamsListResponse(cls._generate_teams_list(teams))

    @classmethod
    def _generate_teams_list(cls, teams_list):
        teams = []

        for team in teams_list:
            teams += [{
                "id": team.team_id,
                "team_name": team.team_name,
                "location": team.location,
                "description": team.description,
                "welcome_message": team.welcome_message,
                "role": team.role
            }]

        return teams
