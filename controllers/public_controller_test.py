"""Tests for public_controller.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import mox

import tiny_classified

import services

import public_controller

TEST_LISTING_1 = {
    'author_email': 'test1@example.com',
    'name': 'TestName1',
    'slugs': ['/cat1/subcat1/TestName1'],
    'about': 'About test listing 1'
}

TEST_LISTING_2 = {
    'author_email': 'test2@example.com',
    'name': 'TestName2',
    'slugs': ['/cat1/subcat1/TestName2', '/cat1/subcat1/TestName2'],
    'about': 'About test listing 2'
}

TEST_LISTINGS = [TEST_LISTING_1, TEST_LISTING_2]

class PublicControllerTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        tiny_classified.app.debug = True
        self.app = tiny_classified.app.test_client()

    def test_index_listings(self):
        self.mox.StubOutWithMock(services.listing_service, 'index')
        services.listing_service.index().AndReturn(TEST_LISTINGS)

        self.mox.ReplayAll()

        result = self.app.get('/public/listings')
        self.assertEqual(200, result.status_code)

    def test_index_listings_by_category_category(self):
        self.mox.StubOutWithMock(
            services.listing_service,
            'list_by_slug'
        )
        services.listing_service.list_by_slug('cat1').AndReturn(
            TEST_LISTINGS
        )

        self.mox.ReplayAll()

        result = self.app.get('/public/listings/cat1')
        self.assertEqual(200, result.status_code)

    def test_index_listings_by_category_category_and_subcategory(self):
        self.mox.StubOutWithMock(
            services.listing_service,
            'list_by_slug'
        )

        url = 'cat1/subcat1'
        services.listing_service.list_by_slug(url).AndReturn(
            TEST_LISTINGS
        )

        self.mox.ReplayAll()

        result = self.app.get('/public/listings/' + url)
        self.assertEqual(200, result.status_code)

    def test_index_listings_by_category_individual(self):
        self.mox.StubOutWithMock(
            services.listing_service,
            'list_by_slug'
        )

        url = 'cat1/subcat1/TestName1'
        services.listing_service.list_by_slug(url).AndReturn(
            TEST_LISTING_1
        )

        self.mox.ReplayAll()

        result = self.app.get('/public/listings/' + url)
        self.assertEqual(200, result.status_code)
