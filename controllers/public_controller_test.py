"""Tests for public_controller.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import copy
import mox

import tiny_classified

import services

import public_controller
import test_util

TEST_LISTING_1 = {
    'author_email': 'test1@example.com',
    'name': 'TestName1',
    'tags': {'cat1':['subcat1']},
    'slugs': ['/cat1/subcat1/TestName1'],
    'about': 'About test listing 1',
    'address': {
        'street': 'example street',
        'city': 'example city',
        'state': 'example state',
        'zip': 'example zip',
    }
}

TEST_LISTING_2 = {
    'author_email': 'test2@example.com',
    'name': 'TestName2',
    'tags': {'cat1':['subcat1', 'subcat2']},
    'slugs': ['/cat1/subcat1/TestName2', '/cat1/subcat2/TestName2'],
    'about': 'About test listing 2'
}

TEST_LISTINGS = [
    TEST_LISTING_1,
    TEST_LISTING_2
]

TEST_TAGS = [
    TEST_LISTING_1['tags'],
    TEST_LISTING_2['tags']
]

TEST_COLLECTED_TAGS_CATEGORY = {
    'cat1': ['subcat1', 'subcat2']
}

TEST_TAGLIST = [
    {'altcategory': ['altsubcat1', 'altsubcat2']},
    {'altcategory': ['altsubcat2', 'altsubcat3']},
    {'category': ['subcat2', 'subcat3']}
]
TEST_INDEX_CATEGORIES = {
    'altcategory': ['altsubcat1', 'altsubcat2', 'altsubcat3'],
    'category': ['subcat2', 'subcat3']
}

class PublicControllerTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        tiny_classified.app.debug = True
        self.app = tiny_classified.app.test_client()

    def test_index_listings(self):
        expected_htmls = ['testhtml', 'otherone']

        self.mox.StubOutWithMock(services.listing_service, 'index_tags')
        services.listing_service.index_tags().AndReturn(TEST_TAGLIST)

        self.mox.StubOutWithMock(services.listing_service, 'collect_index_dict')
        services.listing_service.collect_index_dict(TEST_TAGLIST).AndReturn(
            TEST_INDEX_CATEGORIES)

        self.mox.StubOutWithMock(public_controller, 'render_html_category')
        public_controller.render_html_category(
            mox.IsA(str),
            'altcategory',
            ['altsubcat1', 'altsubcat2', 'altsubcat3']
        ).InAnyOrder().AndReturn('testhmtl')

        public_controller.render_html_category(
            mox.IsA(str),
            'category',
            ['subcat2', 'subcat3']
        ).InAnyOrder().AndReturn('otherone')

        self.mox.ReplayAll()

        result = self.app.get('/public/listings')
        self.assertEqual(200, result.status_code)
        self.assertTrue('testhmtl' in result.data)
        self.assertTrue('otherone' in result.data)

    def test_index_listings_by_slug_category(self):
        test_cursor = test_util.TestCursor(TEST_LISTINGS)
        category = 'cat1'

        self.mox.StubOutWithMock(
            services.listing_service,
            'list_by_slug'
        )
        services.listing_service.list_by_slug(category).AndReturn(
            test_cursor
        )

        self.mox.StubOutWithMock(
            services.listing_service,
            'check_is_qualified_slug'
        )
        services.listing_service.check_is_qualified_slug(category).AndReturn(
            False
        )

        self.mox.StubOutWithMock(services.listing_service, 'collect_index_dict')
        services.listing_service.collect_index_dict(TEST_TAGS).AndReturn(
            TEST_COLLECTED_TAGS_CATEGORY
        )

        self.mox.ReplayAll()

        result = self.app.get('/public/listings/cat1')
        self.assertEqual(200, result.status_code)
        self.assertEqual('tags', test_cursor.distinct_param)

        # Test that expected URLs are in the HTML
        res_html = result.get_data()
        self.assertTrue('/cat1/subcat1' in res_html)
        self.assertTrue('/cat1/subcat2' in res_html)
        self.assertTrue('/cat1/subcat1/TestName1' in res_html)
        self.assertTrue('/cat1/subcat1/TestName2' in res_html)

    def test_index_listings_by_slug_category_and_subcategory(self):
        test_cursor = test_util.TestCursor(TEST_LISTINGS)
        url = 'cat1/subcat1'

        self.mox.StubOutWithMock(
            services.listing_service,
            'list_by_slug'
        )
        services.listing_service.list_by_slug(url).AndReturn(
            test_cursor
        )

        self.mox.StubOutWithMock(
            services.listing_service,
            'check_is_qualified_slug'
        )
        services.listing_service.check_is_qualified_slug(url).AndReturn(
            False
        )

        self.mox.StubOutWithMock(services.listing_service, 'collect_index_dict')
        services.listing_service.collect_index_dict(TEST_TAGS).AndReturn(
            TEST_COLLECTED_TAGS_CATEGORY
        )

        self.mox.ReplayAll()

        result = self.app.get('/public/listings/' + url)
        self.assertEqual(200, result.status_code)
        self.assertEqual('tags', test_cursor.distinct_param)

        # Test that expected URLs are in the HTML
        res_html = result.get_data()
        self.assertTrue('/cat1"' in res_html) # The " makes sure it's the end
        self.assertTrue('/cat1/subcat1/TestName1' in res_html)
        self.assertTrue('/cat1/subcat1/TestName2' in res_html)

        # Expected text
        self.assertTrue('Clear Filters' in res_html)

    def test_index_listings_by_slug_individual(self):
        url = 'cat1/subcat1/TestName1'

        self.mox.StubOutWithMock(services.listing_service, 'list_by_slug')
        services.listing_service.list_by_slug(url).AndReturn(
            test_util.TestCursor([TEST_LISTING_1])
        )

        self.mox.ReplayAll()

        result = self.app.get('/public/listings/' + url)
        self.assertEqual(200, result.status_code)
