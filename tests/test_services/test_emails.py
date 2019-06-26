import unittest
from unittest.mock import MagicMock

from smtplib import SMTPHeloError, SMTPAuthenticationError, SMTPRecipientsRefused

'''Mocking environment properties'''
import sys
sys.modules["smtplib"].SMTP = MagicMock()
sys.modules["logging"].getLogger = MagicMock()

from services.emails import EmailService
mock = MagicMock()


class MockedEmailServer:
    email_sent = False


class EmailTestCase(unittest.TestCase):

    @classmethod
    def mocked_ehlo(cls):
        pass

    @classmethod
    def mocked_starttls(cls):
        pass

    @classmethod
    def mocked_login(cls, user, password):
        pass

    @classmethod
    def mocked_sendmail(cls, from_addr, to_addrs, msg):
        from tests.test_services import test_emails
        MockedEmailServer.email_sent = True

    @classmethod
    def mocked_quit(cls):
        pass

    def setUp(self) -> None:
        MockedEmailServer.email_sent = False

    def test_email_not_sent_when_ehlo_fails(self):
        data = MagicMock()

        def fail():
            raise SMTPHeloError(mock, mock)

        sys.modules["smtplib"].SMTP().ehlo = MagicMock(side_effect=fail)
        sys.modules["smtplib"].SMTP().starttls = MagicMock(side_effect=self.__class__.mocked_starttls)
        sys.modules["smtplib"].SMTP().login = MagicMock(side_effect=self.__class__.mocked_login)
        sys.modules["smtplib"].SMTP().sendmail = MagicMock(side_effect=self.__class__.mocked_sendmail)
        sys.modules["smtplib"].SMTP().quit = MagicMock(side_effect=self.__class__.mocked_quit)

        EmailService.send_email(data)
        self.assertFalse(MockedEmailServer.email_sent)

    def test_email_not_sent_when_authentication_fails(self):
        data = MagicMock()

        def fail(user, password):
            raise SMTPAuthenticationError(mock, mock)

        sys.modules["smtplib"].SMTP().ehlo = MagicMock(side_effect=self.__class__.mocked_ehlo)
        sys.modules["smtplib"].SMTP().starttls = MagicMock(side_effect=self.__class__.mocked_starttls)
        sys.modules["smtplib"].SMTP().login = MagicMock(side_effect=fail)
        sys.modules["smtplib"].SMTP().sendmail = MagicMock(side_effect=self.__class__.mocked_sendmail)
        sys.modules["smtplib"].SMTP().quit = MagicMock(side_effect=self.__class__.mocked_quit)

        EmailService.send_email(data)
        self.assertFalse(MockedEmailServer.email_sent)

    def test_email_not_sent_when_sending_fails(self):
        data = MagicMock()

        def fail(from_addr, to_addrs, msg):
            raise SMTPRecipientsRefused(mock)

        sys.modules["smtplib"].SMTP().ehlo = MagicMock(side_effect=self.__class__.mocked_ehlo)
        sys.modules["smtplib"].SMTP().starttls = MagicMock(side_effect=self.__class__.mocked_starttls)
        sys.modules["smtplib"].SMTP().login = MagicMock(side_effect=self.__class__.mocked_login)
        sys.modules["smtplib"].SMTP().sendmail = MagicMock(side_effect=fail)
        sys.modules["smtplib"].SMTP().quit = MagicMock(side_effect=self.__class__.mocked_quit)

        EmailService.send_email(data)
        self.assertFalse(MockedEmailServer.email_sent)

    def test_email_sent_when_smtplib_works_properly(self):
        data = MagicMock()

        sys.modules["smtplib"].SMTP().ehlo = MagicMock(side_effect=self.__class__.mocked_ehlo)
        sys.modules["smtplib"].SMTP().starttls = MagicMock(side_effect=self.__class__.mocked_starttls)
        sys.modules["smtplib"].SMTP().login = MagicMock(side_effect=self.__class__.mocked_login)
        sys.modules["smtplib"].SMTP().sendmail = MagicMock(side_effect=self.__class__.mocked_sendmail)
        sys.modules["smtplib"].SMTP().quit = MagicMock(side_effect=self.__class__.mocked_quit)

        EmailService.send_email(data)
        self.assertTrue(MockedEmailServer.email_sent)

    def test_recovery_token_email_properly_created(self):
        data = MagicMock()
        data.email = "test@test"
        response = EmailService.recovery_token_message(data)
        self.assertTrue(self.__class__._text_contains(response, "Hypechat\'s Recovery Password Service"))

    def test_team_invitation_email_properly_created(self):
        data = MagicMock()
        data.email = "test@test"
        response = EmailService.team_invitation_message(data)
        self.assertTrue(self.__class__._text_contains(response, "Hypechat\'s Team Service"))

    @classmethod
    def _text_contains(cls, text, elem):
        return text.find(elem) >= 0
