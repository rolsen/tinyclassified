"""Tests for author_controller.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import copy
import json
import mox

import tiny_classified

import services

import author_controller
import util

TEST_EMAIL = 'test@example.com'
TEST_LISTING_NAME = 'TestName'
TEST_SLUG = 'test/slug/TestName'
TEST_LISTING_SLUGS = [TEST_SLUG, 'other/slug/TestName']
TEST_LISTING_ABOUT = 'Test about section'
TEST_LISTING = {
    'author_email': TEST_EMAIL,
    'name': TEST_LISTING_NAME,
    'slugs': TEST_LISTING_SLUGS,
    'about': TEST_LISTING_ABOUT
}

class AuthorControllerTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        tiny_classified.app.debug = True
        self.app = tiny_classified.app.test_client()

    def setup_logged_in(self):
        self.mox.StubOutWithMock(util, 'check_active_requirement')
        util.check_active_requirement().AndReturn(True)

    def test_show_user_ui_not_logged_in(self):
        self.mox.StubOutWithMock(util, 'check_active_requirement')
        util.check_active_requirement().AndReturn(False)
        self.mox.ReplayAll()

        result = self.app.get('/author/')
        self.assertEqual(302, result.status_code)

    def test_show_user_ui_success(self):
        self.setup_logged_in()
        self.mox.ReplayAll()

        result = self.app.get('/author/')
        self.assertEqual(200, result.status_code)
