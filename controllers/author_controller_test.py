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

    def test_create_listing_success(self):
        self.setup_logged_in()

        self.mox.StubOutWithMock(services.listing_service, 'create')
        services.listing_service.create(TEST_LISTING)

        self.mox.ReplayAll()

        test_listing = dict(listing = json.dumps(TEST_LISTING))
        result = self.app.post('/author/create', data=test_listing)
        result_loaded = json.loads(result.data)
        self.assertEqual(TEST_LISTING, result_loaded)

    def test_show_listing_not_exists(self):
        self.setup_logged_in()

        self.mox.StubOutWithMock(services.listing_service, 'list_by_slug')
        services.listing_service.list_by_slug(TEST_SLUG).AndReturn(None)

        self.mox.ReplayAll()

        result = self.app.get('/author/show/%s' % TEST_SLUG)
        self.assertEqual(404, result.status_code)

    def test_show_listing_success(self):
        self.setup_logged_in()

        self.mox.StubOutWithMock(services.listing_service, 'list_by_slug')
        services.listing_service.list_by_slug(TEST_SLUG).AndReturn(
            [TEST_LISTING]
        )

        self.mox.ReplayAll()

        result = self.app.get('/author/show/%s' % TEST_SLUG)
        result_loaded = json.loads(result.data)
        self.assertEqual([TEST_LISTING], result_loaded)

    def test_update_listing_not_exists(self):
        self.setup_logged_in()

        test_updated_listing = copy.deepcopy(TEST_LISTING)
        test_updated_listing['about'] = 'Great new about'

        non_existant_slug = 'non/existant/slug'
        self.mox.StubOutWithMock(services.listing_service, 'update')
        services.listing_service.update(
            non_existant_slug,
            test_updated_listing
        ).AndRaise(ValueError('No listing with slug: ' + non_existant_slug))

        self.mox.ReplayAll()

        test_listing = dict(listing = json.dumps(test_updated_listing))
        test_url = '/author/update/%s' % non_existant_slug
        result = self.app.put(test_url, data=test_listing)
        self.assertEqual(404, result.status_code)

    def test_update_listing_success(self):
        self.setup_logged_in()

        test_updated_listing = copy.deepcopy(TEST_LISTING)
        test_updated_listing['about'] = 'Great new about'

        self.mox.StubOutWithMock(services.listing_service, 'update')
        services.listing_service.update(TEST_SLUG, test_updated_listing)

        self.mox.ReplayAll()

        test_listing = dict(listing = json.dumps(test_updated_listing))
        test_url = '/author/update/%s' % TEST_SLUG
        result = self.app.put(test_url, data=test_listing)
        result_loaded = json.loads(result.data)
        self.assertEqual(test_updated_listing, result_loaded)

    def test_delete_listing_not_exists(self):
        self.setup_logged_in()

        test_slug = 'non/existant/slug'
        self.mox.StubOutWithMock(services.listing_service, 'delete_by_slug')
        services.listing_service.delete_by_slug(test_slug).AndRaise(ValueError)

        self.mox.ReplayAll()

        result = self.app.post('/author/delete/%s' % test_slug)
        self.assertEqual(404, result.status_code)

    def test_delete_listing_success(self):
        self.setup_logged_in()

        self.mox.StubOutWithMock(services.listing_service, 'delete_by_slug')
        services.listing_service.delete_by_slug(TEST_SLUG)

        self.mox.ReplayAll()

        result = self.app.post('/author/delete/%s' % TEST_SLUG)
        self.assertEqual(200, result.status_code)
