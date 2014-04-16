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
        tag_index_html=tag_index_html,
        base_url=tiny_classified.get_config()['BASE_URL'],
    )


@blueprint.route('/listings/<path:category>')
def index_listings_by_category(category):
    """List all listings of a given category.

    @param category: The category for which to list listings.
    @type category: str
    @return: HTML with the listings belonging the the given category.
    @rtype: str
    """
    listings = services.listing_service.list_by_slug(category)

    if len(listings) == 1:
        return flask.render_template(
            'public/individual_listing.html',
            listing=listings[0]
        )
    else:
        return flask.render_template(
            'public/listing_category.html',
            listings=listings
        )
