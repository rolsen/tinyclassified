"""Service for listing CRUD and searching.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import pymongo
import re

from tinyclassified import tiny_classified

DATABASE_NAME = 'tiny_classified'

LISTINGS_COLLECTION_NAME = 'listing'
USERS_COLLECTION_NAME = 'user'

MINIMUM_REQUIRED_LISTING_FIELDS = [
    'author_email',
    'name',
    'slugs',
    'about',
    'tags'
]
ALLOWED_LISTING_FIELDS = [
    '_id',
    'author_email',
    'name',
    'slugs',
    'about',
    'tags',
    'is_published',
    'contact_id_next',
    'contact_infos',
    'address',
    'latitude',
    'longitude',
    'datecreated',
    'datemodified',
    'listingtype'
]

MINIMUM_REQUIRED_USER_FIELDS = ['email', 'password_hash', 'is_admin']

class DBAdapter:
    """Dependency inversion adapter to make db access suck less."""

    def __init__(self):
        """Create a new database adapater around the database engine.

        @param client: The native database wrapper to adapt.
        @type client: flask.ext.pymongo.PyMongo
        """
        app_config = tiny_classified.get_config()
        self.client = pymongo.mongo_client.MongoClient(
            host=app_config['MONGO_HOST'],
            port=app_config['MONGO_PORT'],
        )


    def get_database(self):
        """Get the database for the application.

        @return: Database point provided by the native pymongo.MongoClient
        @rtype: pymongo.database
        """
        return self.client.db[DATABASE_NAME]


    def get_listings_collection(self):
        """Get the database collection for listing information.

        @return: The mongodb database collection used to store listing
            information.
        @rtype: pymongo.collection
        """
        listing_collection = self.get_database()[LISTINGS_COLLECTION_NAME]
        listing_collection.ensure_index('name', unique=True)
        return listing_collection


    def get_users_collection(self):
        """Get the database collection for user information.

        @return: The mongodb database collection used to store user information.
        @rtype: pymongo.collection
        """

        users_collection = self.get_database()[USERS_COLLECTION_NAME]
        users_collection.ensure_index('email', unique=True)
        return users_collection


    def ensure_required_fields(self, record, fields):
        """Ensure a record has a series of fields.

        @param record: The (soon to be saved) database record to check.
        @type record: dict
        @param fields: List of fields that must be present.
        @type fields: list of str
        @raise ValueError: Raised if a field in the fields list is not in
            record.
        """
        for field in fields:
            if not field in record:
                raise ValueError('%s must be in this record.' % field)


    def ensure_limited_fields(self, record, fields):
        """Ensure a record has a only the specified fields.

        @param record: The (soon to be saved) database record to check.
        @type record: dict
        @param fields: The only fields that may be present.
        @type fields: list of str
        @raise ValueError: Raised if a field in the record is not in the fields
            list.
        """
        for field in record:
            if not field in fields:
                raise ValueError('%s not allowed in this record.' % field)


    def index_listings(self):
        """List / index all listings.

        @return: all listings
        @rtype: iterable over dicts
        """
        return self.get_listings_collection().find()


    def get_listing_by_slug(self, listing_slug):
        """Gets a listing which matches the given slug.

        @param listing_slug: The slug to match to a listing.
        @type listing_slug: str
        @return: The matching listing or None
        @rtype: dict or None
        """
        collection = self.get_listings_collection()
        return collection.find_one({'slugs': listing_slug})


    def get_listing_by_name(self, listing_name):
        """Gets a listing which matches the given name.

        @param listing_name: The name to match to a listing.
        @type listing_name: str
        @return: The matching listing or None
        @rtype: dict or None
        """
        collection = self.get_listings_collection()
        return collection.find_one({'name': listing_name})


    def list_listings_by_slug(self, listing_slug):
        """List the listings that have slugs that begin with the specified slug.

        @param listing_slug: The slug to match
        @type listing_slug: str
        @return: The matching listings.
        @rtype: iterable over dicts
        """
        collection = self.get_listings_collection()
        listing_slug = listing_slug.replace('(', '\(')
        listing_slug = listing_slug.replace(')', '\)')
        regex = re.compile('^' + listing_slug, re.IGNORECASE)
        return collection.find({'slugs': regex})


    def upsert_listing(self, listing):
        """Updates or inserts a listing.

        Updates or inserts a listing, with checks for listing validity.

        @param listing: The listing to insert or update. If listing has an "_id"
            then the existing listing with that "_id" is updated, otherwise a
            new listing is inserted.
        @type listing: dict
        """
        self.ensure_required_fields(listing, MINIMUM_REQUIRED_LISTING_FIELDS)
        self.ensure_limited_fields(listing, ALLOWED_LISTING_FIELDS)
        collection = self.get_listings_collection()
        collection.save(listing)


    def delete_listing_by_slug(self, listing_slug):
        """Deletes a listing by one of its fully qualified slugs.

        @param listing_slug: A qualified slug of the listing to delete.
        @type listing_slug: str
        @raises: ValueError if multiple listings are matched by the given slug
            ValueError if no listings are matched by the given slug
        """
        collection = self.get_listings_collection()
        listing_result = collection.find({'slugs': listing_slug})

        count = listing_result.count()
        if count > 1:
            raise ValueError('Slug %s matched multiple listings' % listing_slug)

        if count == 0:
            raise ValueError('Slug %s did match any listings' % listing_slug)

        collection.remove(listing_result.next())


    def delete_listing_by_name(self, listing_name):
        """Deletes a listing.

        @param listing_name: The name of the listing to delete.
        @type listing: str
        """
        collection = self.get_listings_collection()
        collection.remove({'name': listing_name})


    def get_user_by_email(self, user_email):
        """Find a user given an email address.

        @param user_email: The email address of the user to be found.
        @type user_email: str
        @return: The user corresponding to the given email, or None if no user
            is found.
        @rtype: dict
        """
        collection = self.get_users_collection()
        return collection.find_one({'email': user_email})


    def upsert_user(self, user_info):
        """Updates or inserts a user, with checks for user validity.

        @param user: The user to insert or update. If the user has an "_id"
            then the existing user with that "_id" is updated, otherwise a
            new user is inserted.
        @type user: dict
        """
        self.ensure_required_fields(user_info, MINIMUM_REQUIRED_USER_FIELDS)
        collection = self.get_users_collection()
        collection.save(user_info)


    def delete_user(self, user_email):
        """Delete a user given a that user's email address.

        @param user_email: The email address of the user to delete.
        @type user_email: str
        """
        collection = self.get_users_collection()
        collection.remove({'email': user_email})


    def get_tags(self):
        """Get all the unique listing tags.

        @return: All the unique listing tags.
        @type: list
        """
        collection = self.get_listings_collection()
        return collection.distinct('tags')
