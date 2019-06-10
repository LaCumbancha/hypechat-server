class RecoveryPasswordEmailDTO:

    def __init__(self, email, username, token, message_template):
        self.email = email
        self.username = username
        self.token = token
        self.message_template = message_template


class TeamInvitationEmailDTO:

    def __init__(self, email, inviter_name, token, message_template):
        self.email = email
        self.inviter_name = inviter_name
        self.token = token
        self.message_template = message_template


class FacebookUserDTO:

    def __init__(self, facebook_id, email, first_name, last_name, profile_pic):
        self.facebook_id = facebook_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.profile_pic = profile_pic
