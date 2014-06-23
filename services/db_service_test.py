"""Tests for db_service.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import copy

import mox

try:
    from tinyclassified import tiny_classified
except:
    import tiny_classified

import db_service


TEST_LISTING = {
    'author_email': 'test@example.com',
    'name': 'TestName',
    'slugs': ['cat/subcat/TestName'],
    'about': 'Test about'
}

TEST_USER = {
    'email': 'test@example.com',
    'password_hash': 'testpasswordhash',
    'is_admin': False
}

class TestCollection():
    """Test object for injection as a database collection."""
    def __init__(self):
        self.saved = []
        self.deleted = []
        self.indices = []

    def save(self, record):
        self.saved.append(record)

    def remove(self, record):
        self.deleted.append(record)

    def ensure_index(self, key, **kwargs):
        self.indices.append({key: kwargs})

    def find(self, find_dict):
        pass

class TestMongoCursor():
    """Test object for injection as a pymongo.collection.find() result."""
    def __init__(self):
        pass

    def next(self):
        raise StopIteration

    def count(self):
        return 0

class DBAdapterTests(mox.MoxTestBase):

    def setUp(self):
        mox.MoxTestBase.setUp(self)
        self.db_adapter = db_service.DBAdapter()

    def test_get_listings_collection_ensures_unique_names(self):

        test_collection = TestCollection()
        test_database = {db_service.LISTINGS_COLLECTION_NAME: test_collection}

        self.mox.StubOutWithMock(self.db_adapter, 'get_database')
        self.db_adapter.get_database().AndReturn(test_database)

        self.mox.ReplayAll()

        result_collection = self.db_adapter.get_listings_collection()
        self.assertEqual(test_collection, result_collection)
        self.assertTrue({'name': {'unique':True}} in result_collection.indices)

    def test_get_users_collection_ensures_unique_emails(self):
        test_collection = TestCollection()
        test_database = {db_service.USERS_COLLECTION_NAME: test_collection}

        self.mox.StubOutWithMock(self.db_adapter, 'get_database')
        self.db_adapter.get_database().AndReturn(test_database)

        self.mox.ReplayAll()

        result_collection = self.db_adapter.get_users_collection()
        self.assertEqual(test_collection, result_collection)
        self.assertTrue({'email': {'unique':True}} in result_collection.indices)

    def test_ensure_required_fields_not_enough_fields(self):
        test_fields = {'a':'', 'b':'', 'c':''}
        test_record = {'a':'', 'b':''}
        with self.assertRaises(ValueError):
            self.db_adapter.ensure_required_fields(test_record, test_fields)

    def test_ensure_required_fields_exact_fields(self):
        test_fields = {'a':'', 'b':'', 'c':''}
        test_record = {'a':'', 'b':'', 'c':''}
        self.db_adapter.ensure_required_fields(test_record, test_fields)

    def test_ensure_required_fields_extra_fields(self):
        test_fields = {'a':'', 'b':'', 'c':''}
        test_record = {'a':'', 'b':'', 'c':'', 'd':''}
        self.db_adapter.ensure_required_fields(test_record, test_fields)

    def test_ensure_limited_fields_illegal_fields(self):
        test_fields = {'a':'', 'b':''}
        test_record = {'a':'', 'b':'', 'c':''}
        with self.assertRaises(ValueError):
            self.db_adapter.ensure_limited_fields(test_record, test_fields)

    def test_ensure_limited_fields_all_legal_fields(self):
        test_fields = {'a':'', 'b':'', 'c':''}
        test_record = {'a':'', 'b':'', 'c':''}
        self.db_adapter.ensure_limited_fields(test_record, test_fields)

    def test_ensure_limited_fields_subset_legal_fields(self):
        test_fields = {'a':'', 'b':'', 'c':'', 'd':''}
        test_record = {'a':'', 'b':'', 'c':''}
        self.db_adapter.ensure_limited_fields(test_record, test_fields)

    def test_upsert_listing(self):
        test_collection = TestCollection()

        # This is something that we don't care about for now, but may want to
        # enforce later:
        # self.mox.StubOutWithMock(self.db_adapter, 'ensure_required_fields')
        # self.db_adapter.ensure_required_fields(
        #     TEST_LISTING,
        #     db_service.MINIMUM_REQUIRED_LISTING_FIELDS
        # )

        self.mox.StubOutWithMock(self.db_adapter, 'ensure_limited_fields')
        self.db_adapter.ensure_limited_fields(
            TEST_LISTING,
            db_service.ALLOWED_LISTING_FIELDS
        )

        self.mox.StubOutWithMock(self.db_adapter, 'get_listings_collection')
        self.db_adapter.get_listings_collection().AndReturn(test_collection)

        self.mox.ReplayAll()

        self.db_adapter.upsert_listing(TEST_LISTING)
        self.assertTrue(TEST_LISTING in test_collection.saved)

    def test_delete_listing_by_name(self):
        test_collection = TestCollection()

        self.mox.StubOutWithMock(self.db_adapter, 'get_listings_collection')
        self.db_adapter.get_listings_collection().AndReturn(test_collection)

        self.mox.ReplayAll()

        test_name = TEST_LISTING['name']
        self.db_adapter.delete_listing_by_name(test_name)
        self.assertTrue({'name': test_name} in test_collection.deleted)

    def test_delete_listing_by_slug_one_listing(self):
        test_collection = TestCollection()
        test_slug = TEST_LISTING['slugs'][0]
        test_listing = copy.deepcopy(TEST_LISTING)

        test_cursor = TestMongoCursor()

        self.mox.StubOutWithMock(self.db_adapter, 'get_listings_collection')
        self.db_adapter.get_listings_collection().AndReturn(test_collection)

        self.mox.StubOutWithMock(test_collection, 'find')
        test_collection.find({'slugs': test_slug}).AndReturn(test_cursor)

        self.mox.StubOutWithMock(test_cursor, 'count')
        test_cursor.count().AndReturn(1)

        self.mox.StubOutWithMock(test_cursor, 'next')
        test_cursor.next().AndReturn(test_listing)

        self.mox.ReplayAll()

        self.db_adapter.delete_listing_by_slug(test_slug)
        self.assertTrue(test_listing in test_collection.deleted)

    def test_delete_listing_by_slug_no_listings(self):
        test_collection = TestCollection()
        test_slug = TEST_LISTING['slugs'][0]

        test_cursor = TestMongoCursor()

        self.mox.StubOutWithMock(self.db_adapter, 'get_listings_collection')
        self.db_adapter.get_listings_collection().AndReturn(test_collection)

        self.mox.StubOutWithMock(test_collection, 'find')
        test_collection.find({'slugs': test_slug}).AndReturn(test_cursor)

        self.mox.StubOutWithMock(test_cursor, 'count')
        test_cursor.count().AndReturn(0)

        self.mox.ReplayAll()

        with self.assertRaises(ValueError):
            self.db_adapter.delete_listing_by_slug(test_slug)
        self.assertEqual(0, len(test_collection.deleted))

    def test_delete_listing_by_slug_multiple_listings(self):
        test_collection = TestCollection()
        test_slug = TEST_LISTING['slugs'][0]
        test_listing = copy.deepcopy(TEST_LISTING)

        test_cursor = TestMongoCursor()

        self.mox.StubOutWithMock(self.db_adapter, 'get_listings_collection')
        self.db_adapter.get_listings_collection().AndReturn(test_collection)

        self.mox.StubOutWithMock(test_collection, 'find')
        test_collection.find({'slugs': test_slug}).AndReturn(test_cursor)

        self.mox.StubOutWithMock(test_cursor, 'count')
        test_cursor.count().AndReturn(2)

        self.mox.ReplayAll()

        with self.assertRaises(ValueError):
            self.db_adapter.delete_listing_by_slug(test_slug)
        self.assertEqual(0, len(test_collection.deleted))

    def test_upsert_user(self):
        test_collection = TestCollection()

        self.mox.StubOutWithMock(self.db_adapter, 'ensure_required_fields')
        self.db_adapter.ensure_required_fields(
            TEST_USER,
            db_service.MINIMUM_REQUIRED_USER_FIELDS
        )

        self.mox.StubOutWithMock(self.db_adapter, 'get_users_collection')
        self.db_adapter.get_users_collection().AndReturn(test_collection)

        self.mox.ReplayAll()

        self.db_adapter.upsert_user(TEST_USER)
        self.assertTrue(TEST_USER in test_collection.saved)

    def test_delete_user(self):
        test_collection = TestCollection()

        self.mox.StubOutWithMock(self.db_adapter, 'get_users_collection')
        self.db_adapter.get_users_collection().AndReturn(test_collection)

        self.mox.ReplayAll()

        test_email = TEST_USER['email']
        self.db_adapter.delete_user(test_email)
        self.assertTrue({'email': test_email} in test_collection.deleted)
