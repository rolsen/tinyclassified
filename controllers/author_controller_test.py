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
TEST_LISTING_FORM = dict(model = json.dumps(TEST_LISTING))

class AuthorControllerTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        tiny_classified.app.debug = True
        self.app = tiny_classified.app.test_client()
        with self.app.session_transaction() as sess:
            sess[util.SESS_EMAIL] = TEST_EMAIL

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

    def test_update(self):
        self.setup_logged_in()
        test_listing = copy.deepcopy(TEST_LISTING)
        test_listing['is_published'] = True

        self.mox.StubOutWithMock(services.listing_service, 'update')
        services.listing_service.update(test_listing)

        self.mox.ReplayAll()

        response = self.app.put(
            '/author/content',
            data=TEST_LISTING_FORM
        )
        self.assertEqual(200, response.status_code)

    def test_read(self):
        self.setup_logged_in()

        self.mox.StubOutWithMock(services.listing_service, 'read_by_email')
        services.listing_service.read_by_email(TEST_EMAIL)

        self.mox.ReplayAll()

        response = self.app.get('/author/content/_current')
        self.assertEqual(200, response.status_code)
