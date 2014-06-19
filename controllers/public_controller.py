"""Controllers / Flask request handlers for handling public user access.

Controllers / Flask request handlers that support public Internet users
browsing listings.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask
import jinja2

import tinyclassified.tiny_classified as tiny_classified

from .. import services
import util

# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'public',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)


@blueprint.route('/')
def index():
    """List all listings tags.

    @return: HTML with the listing tags index.
    @rtype: str
    """
    config = tiny_classified.get_config()
    
    ignore_front_list = config['NO_FRONT_PAGE_CATEGORIES']

    tags = services.listing_service.index_tags()
    categories = services.listing_service.collect_index_dict(tags)
    categories = dict(filter(
        lambda (key,val): key not in ignore_front_list,
        categories.iteritems()
    ))

    url_base = tiny_classified.get_config()['LISTING_URL_BASE']

    html_categories = [render_html_category(url_base, cat, subcats)
        for cat, subcats in categories.iteritems()]

    return flask.render_template(
        'public/public_index_chrome.html',
        base_url=config['BASE_URL'],
        parent_template=config.get('PARENT_TEMPLATE', 'base.html'),
        html_categories=html_categories
    )


def render_html_category(listing_url_base, category, subcategories):
    """Render the html for a single category of tags.

    @param listing_url_base: The base url.
    @type listing_url_base: str
    @param category: The URL-safe category the subcategory belongs to.
    @type category: str
    @param subcategory: The category's subcategories.
    @type subcategory: iterable over str
    @return: The HTML for a single category
    @rtype: str
    """
    prep = util.prepare_subcategory
    subcategories = [prep(listing_url_base, category, x) for x in subcategories]

    return flask.render_template(
        'public/index_category_inner.html',
        category=category,
        subcategories=subcategories,
        listing_url_base=listing_url_base
    )


@blueprint.route('/<path:slug>')
def index_listings_by_slug(slug):
    """List all listings of a given slug.

    @param slug: The slug for which to list listings.
    @type slug: str
    @return: HTML with the listings belonging the the given slug.
    @rtype: str
    """
    listings = services.listing_service.list_by_slug(slug)
    is_qualified = services.listing_service.check_is_qualified_slug(slug)

    slug_split = slug.split('/')
    category = slug_split[0]

    config = tiny_classified.get_config()

    if listings.count() == 1 and is_qualified:
        return flask.render_template(
            'public/listing_chrome.html',
            base_url=config['BASE_URL'],
            parent_template=config.get('PARENT_TEMPLATE', 'base.html'),
            listing=listings[0],
            category=category,
            listing_url_base=tiny_classified.get_config()['LISTING_URL_BASE'],
            admin=True
        )
    else:
        tags = listings.distinct('tags')
        tags = services.listing_service.collect_index_dict(tags)

        if len(slug_split) > 1:
            subcategories = []
            selected_subcategory = {'name': slug_split[1]}
        else:
            subcategories = tags[category]
            selected_subcategory = None

        url_base = config['LISTING_URL_BASE']

        prep = util.prepare_subcategory
        return flask.render_template(
            'public/category_chrome.html',
            base_url=config['BASE_URL'],
            parent_template=config.get('PARENT_TEMPLATE', 'base.html'),
            category=category,
            listings=listings,
            subcategories=[prep(url_base, category, x) for x in subcategories],
            selected_subcategory=selected_subcategory,
            listing_url_base=url_base
        )
