import os
import smtplib
import logging

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPHeloError, SMTPAuthenticationError, SMTPRecipientsRefused


class EmailService:
    _email_address = os.getenv('EMAIL_ADDRESS')
    _email_password = os.getenv('EMAIL_PASSWORD')

    @classmethod
    def logger(cls):
        return logging.getLogger(cls.__name__)

    @classmethod
    def send_email(cls, data):
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            cls.logger().debug("Starting GMail connection.")
            server.ehlo()
            cls.logger().debug("Starting EHLO.")
            server.starttls()
            cls.logger().debug("Starting TLS.")
            server.login(user=cls._email_address, password=cls._email_password)
            cls.logger().debug("Loging ing to Hypechat email.")
            message = data.message_template(data)
            server.sendmail(from_addr=cls._email_address, to_addrs=data.email, msg=message)
            cls.logger().info(f"Email sent.")
            server.quit()
            cls.logger().debug(f"Quiting Gmail server.")
        except SMTPHeloError:
            cls.logger().error(f"Couldn't sent recovery token due to an Helo error.")
        except SMTPAuthenticationError:
            cls.logger().error(f"Couldn't loging to app email.")
        except SMTPRecipientsRefused:
            cls.logger().error(f"Cannot send recovery token to the specified email address.")

    @classmethod
    def recovery_token_message(cls, recovery_token_data):
        from_address = cls._email_address
        to_address = recovery_token_data.email

        message = MIMEMultipart()
        message['From'] = from_address
        message['To'] = to_address
        message['Subject'] = 'Hypechat\'s Recovery Password Service'
        body = f"Hi {recovery_token_data.username}!\n\nYour recovery token is {recovery_token_data.token}"
        message.attach(MIMEText(body, 'plain'))

        return message.as_string()

    @classmethod
    def team_invitation_message(cls, invitation):
        from_address = cls._email_address
        to_address = invitation.email

        message = MIMEMultipart()
        message['From'] = from_address
        message['To'] = to_address
        message['Subject'] = 'Hypechat\'s Team Service'
        body = f"Hi!\n\nYou've been invited to join team {invitation.team_name} by {invitation.inviter_name}" \
            f". The access token is: {invitation.token}."
        message.attach(MIMEText(body, 'plain'))

        return message.as_string()
