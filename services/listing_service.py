"""Service for listing CRUD and searching.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import jinja2
import os
import re

import tiny_classified

PUBLIC_TEMPLATE_DIR = os.path.join('templates', 'public')
INDEX_TEMPLATE_PATH = os.path.join(
    PUBLIC_TEMPLATE_DIR,
    'listing_tags_index_inner.html'
)
ESCAPED_SLASH = '_slash_'


def make_tag_safe(tag):
    """Convert / modify a tag into a safe version for use as a tag.

    @param tag: The tag or subtag to make safe.
    @type tag: str
    @return: The safe version of the tag.
    @rtype: str
    """
    return tag.replace('/', ESCAPED_SLASH)


def sanitize_tags(listing):
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
    # Put the tags into a list so that newly sanitized tags don't overwrite
    # existing sanitized tags
    tags_temp = []
    for tag in listing['tags']:
        tags_temp.append((
            make_tag_safe(tag),
            [make_tag_safe(subtag) for subtag in listing['tags'][tag]]
        ))

    tags = {}
    for tag, subtags in tags_temp:
        if not tags.get(tag, None):
            tags[tag] = []
        tags[tag].extend(subtags)

    listing['tags'] = tags


def make_slug_safe(slug):
    """Convert / modify a slug substring into a safe version for use in URLs.

    @param slug: The slug substring to make safe.
    @type slug: str
    @return: The safe version of the slug substring.
    @rtype: str
    """
    return slug.replace(' ', '-')


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
    safe_tag = make_slug_safe(tag)
    safe_subtag = make_slug_safe(subtag)
    safe_name = make_slug_safe(name)
    return safe_tag + '/' + safe_subtag + '/' + safe_name


def calculate_slugs(listing):
    """Calculate and update slugs for a listing.

    Calculate the slugs for a listing based on its tags, then add those slugs to
    the given listing.

    @param listing: The listing to calculate and modify.
    @type listing: dict
    """
    slugs = []
    for (tag, subtaglist) in listing['tags'].items():
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
    regex = re.compile("^[\w-]+\/[\w-]+\/[\w@\.-]+$")
    return isinstance(slug, basestring) and regex.match(slug)


def index_tags():
    """List all unique listings tags.

    @return: listing tags as a list of tag dicts
    @rtype: iterable over dicts
    """
    listings = tiny_classified.get_db_adapter().get_listings_collection()
    return listings.distinct('tags')


def collect_index_dict(taglists):
    """Collect the unique categories and subcategories into a dict.

    Compresses lists of listing tags into an intersection in the form of a dict.
    Unique categories are the keys of the resultant dict, which have values of
    lists of listing tag subcategories.

    Example input:
    taglists = [
        {'altcat': ['altsubcat1', 'altsubcat2']}],
        {'altcat': ['altsubcat2', 'altsubcat3']},
        {'cat': ['subcat2', 'subcat3']}
    ]

    example output:
    {
        'altcat': ['altsubcat1', 'altsubcat2', 'altsubcat3'],
        'cat': ['subcat2', 'subcat3']
    }

    @param taglists: The lists of listings tags to collect.
    @type taglists: iterable over dict
    @return: Dict which has unique categories as the keys and lists of listing
    tag subcategories as values.
    @rtype: dict
    """
    categories = {}
    for tags in taglists:
        for category, subcategories in tags.iteritems():
            if categories.get(category, None) == None:
                categories[category] = []
            for subcat in subcategories:
                if not subcat in categories[category]:
                    categories[category].append(subcat)
    return categories


def index_tags_as_html():
    """List all unique listings tags formatted as an HTML document.

    @return: List all unique listings tags formatted as an HTML document.
    @rtype: str
    """
    tags = index_tags()
    categories = collect_index_dict(tags)

    template = None
    with open(INDEX_TEMPLATE_PATH) as f:
        template = jinja2.Template(f.read())

    return template.render({
        'categories': categories,
        'listing_url_base': tiny_classified.get_config()['LISTING_URL_BASE']
    })


def read_by_slug_as_html():
    """Get a listing of all listings formatted as HTML.

    @return: Listing of all listings formatted as an HTML document.
    @rtype: str
    """
    listings = index()

    template = None
    with open(INDEX_TEMPLATE_PATH) as f:
        template = jinja2.Template(f.read())

    return template.render({
        'listings': listings,
        'listing_url_base': util.get_app_config()['LISTING_URL_BASE']
    })


def read_by_slug(qualified_slug):
    """Get the listing corresponding to a qualified listing slug.

    @param qualified_slug: A qualified listing slug corresponding to a listing
    @type qualified_slug: str
    @raise ValueError: If the given slug is not fully qualified.
    """
    ensure_qualified_slug(qualified_slug)
    return tiny_classified.get_db_adapter().get_listing_by_slug(qualified_slug)


def read_by_email(email):
    """Get the listing corresponding to a listing author email address

    @param email: A user / author email address or None if not found
    @type email: str or None
    """
    db_adapter = tiny_classified.get_db_adapter()
    listing_collection = db_adapter.get_listings_collection()
    return listing_collection.find_one({'author_email': email})


def read_contact_by_id(listing, contact_id):
    """Get the contact of a listing, given the contact id.

    @param listing: The listing to search for a contact
    @type listing: dict
    @param contact_id: The id of the contact to find
    @type contact_id: int
    @return: The contact of the listing or None
    @rtype: dict or None
    """
    for contact in listing.get('contact_infos', []):
        if contact.get('_id', None) == contact_id:
            return contact
            break
    return None


def update(listing):
    """Update the listing corresponding to a qualified listing slug.

    @param listing: A listing that already has been saved to the database
    @type listing: dict
    @raise ValueError: If the given listing has not already been saved to the
        database
    """
    if not listing.get('_id', None):
        raise ValueError('Listing not yet saved to database')

    sanitize_tags(listing)
    calculate_slugs(listing)
    tiny_classified.get_db_adapter().upsert_listing(listing)


def delete_by_slug(qualified_slug):
    """Delete a listing by one of its fully qualified slugs.

    @param qualified_slug: A fully qualified slug of the listing to delete.
    @type qualified_slug: str
    @raise ValueError: If the given slug is not fully qualified.
    """
    ensure_qualified_slug(qualified_slug)
    tiny_classified.get_db_adapter().delete_listing_by_slug(qualified_slug)


def delete(listing):
    """Delete a listing from the database.

    Deletes a listing from the database if that listing has been saved to the
    database.

    @param listing: The listing to delete.
    @type listing: dict
    """
    listing_id = listing.get('_id', None)
    if listing_id:
        collection = tiny_classified.get_db_adapter().get_listing_collection()
        collection.remove(listing_id)


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


def create_default_listing_for_user(email):
    """Create a listing for the user corresponding to the given email.

    Create a listing for the user corresponding to the given email,
    initializes the created listing with the user's email address, and saves
    the new listing to the database.

    @param email: An email address corresponding to a user
    @type email: str
    @return: The new listing
    @rtype: dict
    """
    listing = {
        'author_email': email,
        'name': 'Listing for user %s' % email,
        'slugs': [],
        'about': 'About section',
        'tags': []
    }
    tiny_classified.get_db_adapter().upsert_listing(listing)
    return listing
