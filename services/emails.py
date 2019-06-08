import logging


class EmailService:

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def send_email(cls, email_data):
        pass
