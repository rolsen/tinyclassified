"""Service for listing CRUD and searching.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import re

import tiny_classified


def make_string_safe(string):
    """Convert / modify a string into a safe version for use in URLs.

    @param string: The string to make safe.
    @type string: str
    @return: The safe version of the string.
    @rtype: str
    """
    return string.replace(' ', '-')


def make_slug(tag, subtag, name):
    """Constructs a safe slug from the given tag, subtag, and name.

    @param tag: The tag of the slug to be constructed.
    @type tag: str
    @param subtag: The subtag of the slug to be constructed.
    @type subtag: str
    @param name: The name of the slug to be constructed.
    @type name: str
    @return: The slug
    @rtype: str
    """
    safe_tag = make_string_safe(tag)
    safe_subtag = make_string_safe(subtag)
    safe_name = make_string_safe(name)
    return safe_tag + '/' + safe_subtag + '/' + safe_name


def calculate_slugs(listing):
    """Calculate and update slugs for a listing.

    Calculate the slugs for a listing based on its tags, then add those slugs to
    the given listing.

    @param listing: The listing to calculate and modify.
    @type listing: dict
    """
    slugs = []
    for tagdict in listing['tags']:
        for tag, subtaglist in tagdict.iteritems():
            for subtag in subtaglist:
                slugs.append(make_slug(tag, subtag, listing['name']))

    listing['slugs'] = slugs


def ensure_qualified_slug(slug):
    """Ensure the slug is fully qualified by throwing an exception if it is not.

    @param slug: The listing slug to check.
    @type slug: str
    @raise ValueError: If the given slug is not fully qualified.
    """
    if not check_is_qualified_slug(slug):
        raise ValueError('%s is not a fully qualified slug' % slug)


def check_is_qualified_slug(slug):
    """Check if a listing slug is fully qualified or not.

    Check if a listing slug is fully qualified or not, where a fully qualified
    slug looks like this: "category/sub-category/name-of-listing".

    @param slug: The listing slug to check.
    @type slug: str
    @return: True if the slug is fully qualified, False if not
    @rtype: boolean
    """
    regex = re.compile("^[\w-]+\/[\w-]+\/[\w-]+$")
    return isinstance(slug, basestring) and regex.match(slug)


def index():
    """List all listings.

    @return: listings
    @rtype: iterable over dict
    """
    return tiny_classified.get_db_adapter().index_listings()


def read_by_slug(qualified_slug):
    """Get the listing corresponding to a qualified listing slug.

    @param qualified_slug: A qualified listing slug corresponding to a listing
    @type qualified_slug: str
    @raise ValueError: If the given slug is not fully qualified.
    """
    ensure_qualified_slug(qualified_slug)
    return tiny_classified.get_db_adapter().get_listing_by_slug(qualified_slug)


def update(qualified_slug, listing):
    """Update the listing corresponding to a qualified listing slug.

    @param qualified_slug: A qualified listing slug corresponding to a listing
    @type qualified_slug: str
    @raise ValueError: If the given slug is not fully qualified or if no listing
        is found with the given slug.
    """
    original_listing = read_by_slug(qualified_slug)

    if not original_listing:
        raise ValueError('No listing with slug: ' + qualified_slug)

    calculate_slugs(listing)

    listing['_id'] = original_listing['_id']

    tiny_classified.get_db_adapter().upsert_listing(listing)


def delete_by_slug(qualified_slug):
    """Delete a listing by one of its fully qualified slugs.

    @param qualified_slug: A fully qualified slug of the listing to delete.
    @type qualified_slug: str
    @raise ValueError: If the given slug is not fully qualified.
    """
    ensure_qualified_slug(qualified_slug)
    tiny_classified.get_db_adapter().delete_listing_by_slug(qualified_slug)


def create(listing):
    """Create a new listing and persist it to the database.

    @param listing: The new listing to save
    @param listing: dict
    @raise ValueError: If a listing with the same name as the new listing
        already exists.
    """
    if tiny_classified.get_db_adapter().get_listing_by_name(listing.name):
        raise ValueError('Listing with name %s already exists.' % name)

    calculate_slugs(listing)
    tiny_classified.get_db_adapter().upsert_listing(listing)


def list_by_slug(slug):
    """Determines if a specific listing should be returned or a listing index.

    If this slug refers to a specific listing, returns that single listing.
    Otherwise, returns a list of listings that have this slug as their prefix
    or, in other words, the listings under the category / sub-category that
    this slug refers to.

    @param slug: The slug to look up.
    @type slug: str
    @return: The individual listing or the list of listings at this slug. Will
        be a list if this refers to a cateogry / sub-category. Will be a list of
        one element if this slug refers to a single listing.
    @rtype: list
    """
    return tiny_classified.get_db_adapter().list_listings_by_slug(slug)
