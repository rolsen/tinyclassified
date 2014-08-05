"""Controllers / Flask request handlers for handling public user access.

Controllers / Flask request handlers that support public Internet users
browsing listings.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask
import jinja2
import markdown

# Optimally, it would be nice to have "is_module" controlled by the configs, but
# they may not be available when this module is imported.
is_module = True

try:
    from tinyclassified import tiny_classified
    from tinyclassified import services
except:
    import tiny_classified
    import services
    is_module = False

import util


# Create a Flask blueprint to split the Flask routes among multiple files.
blueprint = flask.Blueprint(
    'public',
    __name__,
    **util.get_blueprint_folders(is_module)
)


@blueprint.route('/confirm_delete')
def confirm_delete():
    config = tiny_classified.get_config()
    temp_vals = tiny_classified.render_common_template_vals()
    parent_template = config.get(
        'PARENT_TEMPLATE',
        'tinyclassified_base.html'
    )

    return flask.render_template(
        'public/deleted_confirmation.html',
        base_url=config['BASE_URL'],
        parent_template=parent_template,
        **temp_vals
    )


@blueprint.route('/')
def index():
    """List all listings tags.

    @return: HTML with the listing tags index.
    @rtype: str
    """
    config = tiny_classified.get_config()

    tags = services.listing_service.index_tags()
    categories = services.listing_service.collect_index_dict(
        tags,
        home_only=True
    )

    url_base = tiny_classified.get_config()['LISTING_URL_BASE']

    html_categories = [render_html_category(url_base, cat, subcats)
        for cat, subcats in categories.iteritems()]

    temp_vals = tiny_classified.render_common_template_vals()
    temp_vals.update({"top_ad_target": "Resources", "side_ad_1_target": "Resources", "side_ad_2_target": "Resources"})

    parent_template = config.get(
        'PARENT_TEMPLATE',
        'tinyclassified_base.html'
    )

    return flask.render_template(
        'public/public_index_chrome.html',
        base_url=config['BASE_URL'],
        parent_template=parent_template,
        html_categories=html_categories,
        **temp_vals
    )


def render_html_category(listing_url_base, category, subcategories):
    """Render the html for a single category of tags.

    @param listing_url_base: The base url.
    @type listing_url_base: str
    @param category: The URL-safe category the subcategory belongs to.
    @type category: str
    @param subcategories: The category's subcategories.
    @type subcategories: iterable over str
    @return: The HTML for a single category
    @rtype: str
    """
    prep = util.prepare_subcategory
    prep_subcats = [prep(listing_url_base, category, x) for x in subcategories]

    temp_vals = tiny_classified.render_common_template_vals()

    return flask.render_template(
        'public/index_category_inner.html',
        category=category,
        subcategories=prep_subcats,
        listing_url_base=listing_url_base,
        **temp_vals
    )


def index_listings_by_slug_programmatic(slug, parent_template, temp_vals, home):
    listings = services.listing_service.list_by_slug(slug)

    slug_split = slug.split('/')
    category = slug_split[0]

    config = tiny_classified.get_config()

    if listings.count() == 0:
        return None

    listing = listings[0]
    is_qualified = services.listing_service.check_is_qualified(listing, slug)

    about = listing.get('about', None)
    if about:
        about = markdown.markdown(about)

    if listings.count() == 1 and is_qualified:
        return flask.render_template(
            'public/listing_chrome.html',
            base_url=config['BASE_URL'],
            parent_template=parent_template,
            listing=listing,
            category=category,
            about=about,
            listing_url_base=tiny_classified.get_config()['LISTING_URL_BASE'],
            admin=util.check_admin_requirement(True),
            **temp_vals
        )
    else:
        tags = listings.distinct('tags')
        tags = services.listing_service.collect_index_dict(tags, home_only=home)

        if len(slug_split) > 1:
            subcategories = []
            selected_subcategory = {'name': slug_split[1]}
        else:
            subcategories = tags[category]
            selected_subcategory = None

        url_base = config['LISTING_URL_BASE']

        listings = list(listings)
        featured_listings = sorted(filter(
            lambda x: x.get('featured', False),
            listings
        ), key=lambda x: x['name'])

        prep = util.prepare_subcategory
        return flask.render_template(
            'public/category_chrome.html',
            base_url=config['BASE_URL'],
            parent_template=parent_template,
            category=category,
            listings=listings,
            featured_listings=featured_listings,
            subcategories=[prep(url_base, category, x) for x in subcategories],
            selected_subcategory=selected_subcategory,
            listing_url_base=url_base,
            **temp_vals
        )


@blueprint.route('/<path:slug>')
def index_listings_by_slug(slug):
    """List all listings of a given slug.

    @param slug: The slug for which to list listings.
    @type slug: str
    @return: HTML with the listings belonging the the given slug.
    @rtype: str
    """
    config = tiny_classified.get_config()
    temp_vals = tiny_classified.render_common_template_vals(
        'resources/' + slug
    )

    parent_template = config.get(
        'PARENT_TEMPLATE',
        'tinyclassified_base.html'
    )

    result = index_listings_by_slug_programmatic(
        slug,
        parent_template,
        temp_vals,
        True
    )

    if not result:
        flask.abort(404)

    return result
