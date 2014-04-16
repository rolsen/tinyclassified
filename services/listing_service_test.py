"""Tests for listing_service.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import copy
import mox
import pymongo

import tiny_classified

import controllers

import db_service
import listing_service

ALL_CHARS_STR = '0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]\
^_`abcdefghijklmnopqrstuvwxyz/'

TEST_EMAIL = 'test@example.com'
TEST_NAME = 'TestName'
TEST_TAG1 = 'cat1'
TEST_TAG2 = 'other2'
TEST_SUBTAG1 = 'subcat1'
TEST_SUBTAG2 = 'submeow2'
TEST_SUBTAG3 = 'subother3'
TEST_TAGS_SIMPLE = [{TEST_TAG1: [TEST_SUBTAG1]}]
TEST_TAGS_MULTIPLE_SUB_TAGS = [{TEST_TAG1: [TEST_SUBTAG1, TEST_SUBTAG2]}]
TEST_TAGS_MULTIPLE_TAGS = [
    {TEST_TAG1: [TEST_SUBTAG1, TEST_SUBTAG2]},
    {TEST_TAG2: [TEST_SUBTAG3]}
]
TEST_SLUG1 = 'cat1/subcat1/TestName'

TEST_LISTING = {
    'author_email': TEST_EMAIL,
    'name': TEST_NAME,
    'slugs': [TEST_SLUG1],
    'about': 'Test about',
    'tags': TEST_TAGS_SIMPLE
}

TEST_LISTING_ALT = {
    'author_email': 'alt@example.com',
    'name': 'Alt Listing Name',
    'slugs': ['cat1/subcat1/Alt Listing Name'],
    'about': 'Alt about',
    'tags': [{'altcat': ['altsubcat1', 'altsubcat2']}]
}
TEST_LISTINGS = [TEST_LISTING, TEST_LISTING_ALT]

TEST_TAGLIST = [
    {'altcategory': ['altsubcat1', 'altsubcat2']},
    {'altcategory': ['altsubcat2', 'altsubcat3']},
    {'category': ['subcat2', 'subcat3']}
]
TEST_INDEX_CATEGORIES = {
    'altcategory': ['altsubcat1', 'altsubcat2', 'altsubcat3'],
    'category': ['subcat2', 'subcat3']
}

class ListingServiceTests(mox.MoxTestBase):

    def test_make_string_safe_no_spaces(self):
        result = listing_service.make_string_safe(ALL_CHARS_STR)
        self.assertEqual(ALL_CHARS_STR, result)

    def test_make_string_safe_spaces(self):
        test_str = "test string"
        result = listing_service.make_string_safe(test_str)

        safe_str = "test-string"
        self.assertEqual(safe_str, result)

    def test_make_slug(self):
        self.mox.StubOutWithMock(listing_service, 'make_string_safe')
        listing_service.make_string_safe(TEST_NAME).InAnyOrder().AndReturn(
            TEST_NAME
        )
        listing_service.make_string_safe(TEST_TAG1).InAnyOrder().AndReturn(
            TEST_TAG1
        )
        listing_service.make_string_safe(TEST_SUBTAG1).InAnyOrder().AndReturn(
            TEST_SUBTAG1
        )

        self.mox.ReplayAll()

        result = listing_service.make_slug(TEST_TAG1, TEST_SUBTAG1, TEST_NAME)
        self.assertEqual('cat1/subcat1/TestName', result)

    def test_calculate_slugs_simple(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_listing['slugs'] = []

        self.mox.StubOutWithMock(listing_service, 'make_slug')
        listing_service.make_slug(TEST_TAG1, TEST_SUBTAG1, TEST_NAME).AndReturn(
            'cat1/subcat1/TestName'
        )

        self.mox.ReplayAll()

        listing_service.calculate_slugs(test_listing)
        self.assertEqual(['cat1/subcat1/TestName'], test_listing['slugs'])

    def test_calculate_slugs_multiple_subtags(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_listing['slugs'] = []
        test_listing['tags'] = TEST_TAGS_MULTIPLE_SUB_TAGS

        self.mox.StubOutWithMock(listing_service, 'make_slug')
        listing_service.make_slug(TEST_TAG1, TEST_SUBTAG1, TEST_NAME).AndReturn(
            'cat1/subcat1/TestName'
        )
        listing_service.make_slug(TEST_TAG1, TEST_SUBTAG2, TEST_NAME).AndReturn(
            'cat1/submeow2/TestName'
        )

        self.mox.ReplayAll()

        listing_service.calculate_slugs(test_listing)
        expected_slugs = ['cat1/subcat1/TestName', 'cat1/submeow2/TestName']
        self.assertEqual(expected_slugs, test_listing['slugs'])

    def test_calculate_slugs_multiple_tags(self):
        test_listing = copy.deepcopy(TEST_LISTING)
        test_listing['slugs'] = []
        test_listing['tags'] = TEST_TAGS_MULTIPLE_TAGS

        self.mox.StubOutWithMock(listing_service, 'make_slug')
        listing_service.make_slug(TEST_TAG1, TEST_SUBTAG1, TEST_NAME).AndReturn(
            'cat1/subcat1/TestName'
        )
        listing_service.make_slug(TEST_TAG1, TEST_SUBTAG2, TEST_NAME).AndReturn(
            'cat1/submeow2/TestName'
        )
        listing_service.make_slug(TEST_TAG2, TEST_SUBTAG3, TEST_NAME).AndReturn(
            'other2/subother3/TestName'
        )

        self.mox.ReplayAll()

        listing_service.calculate_slugs(test_listing)
        expected_slugs = [
            'cat1/subcat1/TestName',
            'cat1/submeow2/TestName',
            'other2/subother3/TestName'
        ]
        self.assertEqual(expected_slugs, test_listing['slugs'])

    def test_ensure_qualified_slug_qualified(self):
        self.mox.StubOutWithMock(listing_service, 'check_is_qualified_slug')
        listing_service.check_is_qualified_slug('cat/sub/name').AndReturn(True)

        self.mox.ReplayAll()
        listing_service.ensure_qualified_slug('cat/sub/name')

    def test_ensure_qualified_slug_not_qualified(self):
        self.mox.StubOutWithMock(listing_service, 'check_is_qualified_slug')
        listing_service.check_is_qualified_slug('blahblah').AndReturn(False)

        self.mox.ReplayAll()
        with self.assertRaises(ValueError):
            listing_service.ensure_qualified_slug('blahblah')

    def test_check_is_qualified_slug_two_slashes(self):
        result = listing_service.check_is_qualified_slug('category/subcat')
        self.assertFalse(result)

    def test_check_is_qualified_slug_skipped_category(self):
        result = listing_service.check_is_qualified_slug('/subcategory/name')
        self.assertFalse(result)

    def test_check_is_qualified_slug_ok(self):
        result = listing_service.check_is_qualified_slug('categor/subcat/name')
        self.assertTrue(result)

    def test_check_is_qualified_slug_ok_with_dashes(self):
        result = listing_service.check_is_qualified_slug('cat-go/sub-ct/na-me')
        self.assertTrue(result)

    def test_collect_index_dict(self):
        actual_result = listing_service.collect_index_dict(TEST_TAGLIST)
        self.assertEqual(TEST_INDEX_CATEGORIES, actual_result)

    def test_index_tags_as_html(self):
        self.mox.StubOutWithMock(listing_service, 'index_tags')
        listing_service.index_tags().AndReturn(TEST_TAGLIST)

        self.mox.StubOutWithMock(listing_service, 'collect_index_dict')
        listing_service.collect_index_dict(TEST_TAGLIST).AndReturn(
            TEST_INDEX_CATEGORIES)

        self.mox.ReplayAll()

        result = listing_service.index_tags_as_html()
        self.assertTrue('altcategory' in result)
        self.assertTrue('altsubcat1' in result)
        self.assertTrue('altsubcat2' in result)
        self.assertTrue('altsubcat3' in result)
        self.assertTrue('category' in result)
        self.assertTrue('subcat2' in result)
        self.assertTrue('subcat3' in result)

    def test_read_by_slug_ensures_qualified(self):
        self.mox.StubOutWithMock(listing_service, 'ensure_qualified_slug')
        listing_service.ensure_qualified_slug(TEST_SLUG1)

        test_db_adapter = mox.Mox().CreateMock(db_service.DBAdapter)
        test_db_adapter.get_listing_by_slug(TEST_SLUG1)
        tiny_classified.db_adapter = test_db_adapter

        self.mox.ReplayAll()

        listing_service.read_by_slug(TEST_SLUG1)

    def test_read_by_email_not_found(self):
        test_collection = controllers.test_util.TestCollection()
        test_collection.find_result = None

        test_db_adapter = controllers.test_util.TestDBAdapter()
        test_db_adapter.collection = test_collection

        self.mox.StubOutWithMock(tiny_classified, 'get_db_adapter')
        tiny_classified.get_db_adapter().AndReturn(test_db_adapter)

        self.mox.ReplayAll()

        result = listing_service.read_by_email(TEST_EMAIL)
        self.assertEqual(None, result)
        expected_find_hash = {'author_email': TEST_EMAIL}
        self.assertTrue(controllers.test_util.check_dict(
            expected_find_hash,
            test_collection.find_hash
        ))

    def test_read_by_email_found(self):
        test_collection = controllers.test_util.TestCollection()
        test_collection.find_result = TEST_LISTING

        test_db_adapter = controllers.test_util.TestDBAdapter()
        test_db_adapter.collection = test_collection

        self.mox.StubOutWithMock(tiny_classified, 'get_db_adapter')
        tiny_classified.get_db_adapter().AndReturn(test_db_adapter)

        self.mox.ReplayAll()

        result = listing_service.read_by_email(TEST_EMAIL)
        self.assertTrue(controllers.test_util.check_dict(
            TEST_LISTING,
            result
        ))
        expected_find_hash = {'author_email': TEST_EMAIL}
        self.assertTrue(controllers.test_util.check_dict(
            expected_find_hash,
            test_collection.find_hash
        ))

    def test_update_not_yet_saved(self):
        test_listing_new = copy.deepcopy(TEST_LISTING)

        with self.assertRaises(ValueError):
            listing_service.update(test_listing_new)

    def test_update_saved(self):
        test_id = 'someid'
        test_listing_copy = copy.deepcopy(TEST_LISTING)
        test_listing_copy['_id'] = test_id
        test_listing_new = copy.deepcopy(TEST_LISTING)
        test_listing_new['_id'] = test_id

        self.mox.StubOutWithMock(listing_service, 'calculate_slugs')
        listing_service.calculate_slugs(test_listing_new)

        test_db_adapter = mox.Mox().CreateMock(db_service.DBAdapter)
        test_db_adapter.upsert_listing(test_listing_new)
        tiny_classified.db_adapter = test_db_adapter

        self.mox.ReplayAll()

        listing_service.update(test_listing_new)
        self.assertEqual(test_id, test_listing_new['_id'])
        self.assertEqual(test_listing_new, test_listing_copy)
