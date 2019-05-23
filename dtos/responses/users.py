from models.constants import UserStatus


class SuccessfulUserRequestResponse:

    def __init__(self, user):
        self.status = UserStatus.ACTIVE.value
        self.user = ActiveUserResponse(user)

    def json(self):
        return {
            "status": self.status,
            "user": self.user.json()
        }


class ActiveUserResponse:

    def __init__(self, user):
        self.username = user.username
        self.email = user.email
        self.first_name = user.first_name
        self.last_name = user.last_name
        self.profile_pic = user.profile_pic

    def json(self):
        return vars(self)
