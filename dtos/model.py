class RecoveryPasswordEmailDTO:

    def __init__(self, email, username, token):
        self.email = email
        self.username = username
        self.token = token
