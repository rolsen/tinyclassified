"""Unit tests related to email service logic.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@author: Sam Pottinger (samnsparky, Gleap LLC 2014)
"""

import unittest

import mox
import sendgrid

import tiny_classified

import email_service

class TestWebComponent:
    def __init__(self):
        self.message = None

    def send(self, message):
        self.message = message


class TestEmailService:
    def __init__(self):
        self.web = TestWebComponent()


class EmailTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        tiny_classified.get_config()['FAKE_EMAIL'] = False

    def test_send(self):
        test_service = TestEmailService()
        self.mox.StubOutWithMock(email_service, 'get_service_client')
        email_service.get_service_client(
            tiny_classified.get_config()['EMAIL_USERNAME'],
            tiny_classified.get_config()['EMAIL_PASSWORD'],
            tiny_classified.get_config()['EMAIL_USE_SECURE'],
        ).AndReturn(test_service)
        self.mox.ReplayAll()

        email_service.send(
            ['recipient@example.com'],
            'subject',
            'plain_body',
            'html_body'
        )

        message = test_service.web.message
        mesg_dict = message.__dict__
        self.assertEqual(
            mesg_dict['from_email'],
            tiny_classified.get_config()['EMAIL_FROM_ADDR']
        )
        self.assertEqual(mesg_dict['to'], ['recipient@example.com'])
        self.assertEqual(mesg_dict['subject'], 'subject')
        self.assertEqual(mesg_dict['text'], 'plain_body')
        self.assertEqual(mesg_dict['html'], 'html_body')

    def test_send_only_plain(self):
        test_service = TestEmailService()
        self.mox.StubOutWithMock(email_service, 'get_service_client')
        email_service.get_service_client(
            tiny_classified.get_config()['EMAIL_USERNAME'],
            tiny_classified.get_config()['EMAIL_PASSWORD'],
            tiny_classified.get_config()['EMAIL_USE_SECURE'],
        ).AndReturn(test_service)
        self.mox.ReplayAll()

        email_service.send(
            ['recipient@example.com'],
            'subject',
            '**plain_body**'
        )

        message = test_service.web.message
        mesg_dict = message.__dict__
        self.assertEqual(
            mesg_dict['from_email'],
            tiny_classified.get_config()['EMAIL_FROM_ADDR']
        )
        self.assertEqual(mesg_dict['to'], ['recipient@example.com'])
        self.assertEqual(mesg_dict['subject'], 'subject')
        self.assertEqual(mesg_dict['text'], '**plain_body**')
        self.assertEqual(mesg_dict['html'], '<p><strong>plain_body</strong></p>')
