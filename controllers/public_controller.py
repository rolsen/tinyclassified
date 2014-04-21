"""Controllers / Flask request handlers for handling public user access.

Controllers / Flask request handlers that support public Internet users
browsing listings.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask

import tiny_classified

import services

# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'public',
    __name__,
    template_folder='templates'
)


@blueprint.route('/listings')
def index():
    """List all listings tags.

    @return: HTML with the listing tags index.
    @rtype: str
    """
    tag_index_html = services.listing_service.index_tags_as_html()
    return flask.render_template(
        'public/public_index_chrome.html',
        listing_tags_index_inner=tag_index_html,
        base_url=tiny_classified.get_config()['BASE_URL']
    )


@blueprint.route('/listings/<path:slug>')
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

    if listings.count() == 1 and is_qualified:
        return flask.render_template(
            'public/listing_chrome.html',
            listing=listings[0],
            category=category,
            listing_url_base=tiny_classified.get_config()['LISTING_URL_BASE'],
        )
    else:
        tags = listings.distinct('tags')
        tags = services.listing_service.collect_index_dict(tags)

        if len(slug_split) > 1:
            subcategories = slug_split[1]
            subcat_filter = True
        else:
            subcategories = tags[category]
            subcat_filter = False

        return flask.render_template(
            'public/category_chrome.html',
            category=category,
            listings=listings,
            subcategories=subcategories,
            subcat_filter=subcat_filter,
            listing_url_base=tiny_classified.get_config()['LISTING_URL_BASE'],
        )
