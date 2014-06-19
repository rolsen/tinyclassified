"""Controllers for handling each author's CRUD functionality for listings.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import json

import flask

from bson import BSON
from bson import json_util

import tiny_classified

import services

import util

# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'author',
    __name__,
    template_folder='templates'
)

@blueprint.route('/')
@util.require_login()
def show_user_ui():
    """Render the chrome (UI constructs) for user / author controls.

    @return {String} Rendered HTML template with the author control interface.
    """
    listing_view_templates = flask.render_template(
        'author/listing_view.html'
    )
    contacts_view_templates = flask.render_template(
        'author/contacts_view.html'
    )
    listing_about_templates = flask.render_template(
        'author/listing_about.html'
    )

    return flask.render_template(
        'author/author_chrome.html',
        listing_view_templates=listing_view_templates,
        contacts_view_templates=contacts_view_templates,
        listing_about_templates=listing_about_templates,
        email=flask.session[util.SESS_EMAIL],
        base_url=tiny_classified.get_config()['BASE_URL']
    )


def is_admin():
    return True


@blueprint.route('/content/<email>')
@util.require_login()
def read(email):
    """Get the current user's listing through the JSON-REST API.

    @return: JSON-encoded document describing the user's listing.
    @rtype: str
    """
    if not is_admin() or email == '_current':
        email = flask.session.get(util.SESS_EMAIL, None).lower()
    listing = services.listing_service.read_by_email(email)

    result_dict = listing
    return json.dumps(result_dict, default=json_util.default)


@blueprint.route('/content/<update_param>', methods=['PUT', 'POST'])
@util.require_login()
def update(update_param):
    """Update the current user's listing through the JSON-REST API.

    @return: JSON-encoded document describing the user's listing.
    @rtype: str
    """
    listing = json.loads(
        flask.request.form.get('model'),
        object_hook=json_util.object_hook
    )

    if is_admin():
        listing['is_published'] = True

    services.listing_service.update(listing)

    result_dict = listing
    return json.dumps(result_dict, default=json_util.default)
