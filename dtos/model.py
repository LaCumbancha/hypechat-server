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
