"""Tests for author_contact_controller.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import copy
import json
import mox

import tiny_classified

import services

import author_contact_controller
import test_util
import util

TEST_EMAIL = 'test@example.com'
TEST_TYPE = 'phone'
TEST_PHONE = '(123)-456-7890'
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

TEST_CONTACT = {
    'type': TEST_TYPE,
    'value': TEST_PHONE,
    '_id': 0
}
TEST_CONTACT_NO_ID = {
    'type': TEST_TYPE,
    'value': TEST_PHONE
}
TEST_FORM = dict(model = json.dumps(TEST_CONTACT_NO_ID))

class AuthorContactControllerTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        tiny_classified.app.debug = True
        self.app = tiny_classified.app.test_client()
        with self.app.session_transaction() as sess:
            sess[util.SESS_EMAIL] = TEST_EMAIL

    def test_create_no_prior(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_db_adapter = test_util.TestDBAdapter()
        listing_collection = test_util.TestCollection()
        listing_collection.find_result = test_listing
        test_db_adapter.collection = listing_collection

        self.mox.StubOutWithMock(tiny_classified, 'get_db_adapter')
        tiny_classified.get_db_adapter().AndReturn(test_db_adapter)

        self.mox.StubOutWithMock(services.listing_service, 'update')
        services.listing_service.update(test_listing)

        self.mox.ReplayAll()

        response = self.app.post('/author/content/contact', data=TEST_FORM)
        self.assertEqual(200, response.status_code)
        self.assertTrue(test_listing['contact_infos'])
        self.assertEqual(1, len(test_listing['contact_infos']))
        self.assertEqual(1, test_listing['contact_id_next'])

        data_response = json.loads(response.data)

        self.assertTrue(test_util.check_dict(
            TEST_CONTACT,
            data_response
        ))

    def test_index(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_contacts = [TEST_CONTACT]
        test_listing['contact_infos'] = test_contacts

        self.mox.StubOutWithMock(services.listing_service, 'read_by_email')
        services.listing_service.read_by_email(TEST_EMAIL).AndReturn(
            test_listing
        )
        self.mox.ReplayAll()

        response = self.app.get('/author/content/contact')
        contact_infos = json.loads(response.data)['contact_infos']
        self.assertEqual(1, len(contact_infos))
        self.assertTrue(test_util.check_dict(
            TEST_CONTACT,
            contact_infos[0]
        ))

    def test_read_no_contacts(self):
        self.mox.StubOutWithMock(services.listing_service, 'read_by_email')
        services.listing_service.read_by_email(TEST_EMAIL).AndReturn(
            TEST_LISTING
        )

        self.mox.ReplayAll()

        response = self.app.get('/author/content/contact/1')
        self.assertEqual(response.status_code, 404)

    def test_read_missing_id(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_listing['contact_infos'] = [TEST_CONTACT]

        self.mox.StubOutWithMock(services.listing_service, 'read_by_email')
        services.listing_service.read_by_email(TEST_EMAIL).AndReturn(
            test_listing
        )

        self.mox.ReplayAll()

        response = self.app.get('/author/content/contact/3')
        self.assertEqual(response.status_code, 404)

    def test_read(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_listing['contact_infos'] = [TEST_CONTACT]

        self.mox.StubOutWithMock(services.listing_service, 'read_by_email')
        services.listing_service.read_by_email(TEST_EMAIL).AndReturn(
            test_listing
        )

        self.mox.ReplayAll()

        response = self.app.get('/author/content/contact/0')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(test_util.check_dict(
            TEST_CONTACT,
            json.loads(response.data)['contact']
        ))

    def test_delete(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_listing['contact_infos'] = [TEST_CONTACT]

        self.mox.StubOutWithMock(services.listing_service, 'read_by_email')
        services.listing_service.read_by_email(TEST_EMAIL).AndReturn(
            test_listing
        )

        self.mox.StubOutWithMock(util, 'remove_element_by_id')
        util.remove_element_by_id(test_listing['contact_infos'], 0).AndReturn(
            True
        )

        self.mox.StubOutWithMock(services.listing_service, 'update')
        services.listing_service.update(mox.IsA(dict))

        self.mox.ReplayAll()

        response = self.app.delete('/author/content/contact/0')
        self.assertTrue(200, response.status_code)

    def test_index(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_listing['contact_infos'] = [TEST_CONTACT]

        self.mox.StubOutWithMock(services.listing_service, 'read_by_email')
        services.listing_service.read_by_email(TEST_EMAIL).AndReturn(
            test_listing
        )
        self.mox.ReplayAll()

        response = self.app.get('/author/content/contact')
        self.assertEqual(
            [TEST_CONTACT],
            json.loads(response.data)
        )
