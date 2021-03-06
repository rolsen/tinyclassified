"""Controllers for handling each author's CRUD functionality for listings.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import json

import flask

from bson import BSON
from bson import json_util

try:
    from tinyclassified import tiny_classified
    from tinyclassified import services
except:
    import tiny_classified
    import services

import util

# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'author',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

@blueprint.route('/')
@util.require_login()
def show_user_ui():
    """Render the chrome (UI constructs) for user / author controls.

    @return: Rendered HTML template with the author control interface.
    @rtype: str
    """
    config = tiny_classified.get_config()
    temp_vals = tiny_classified.render_common_template_vals()
    parent_template = config.get(
        'PARENT_TEMPLATE',
        'tinyclassified_base.html'
    )

    listing_view_templates = flask.render_template(
        'author/listing_view.html',
        parent_template=parent_template,
        base_url=config['BASE_URL']
    )
    contacts_view_templates = flask.render_template(
        'author/contacts_view.html',
        parent_template=parent_template,
        base_url=config['BASE_URL']
    )
    listing_about_templates = flask.render_template(
        'author/listing_about.html',
        parent_template=parent_template,
        base_url=config['BASE_URL']
    )

    return flask.render_template(
        'author/author_chrome.html',
        parent_template=parent_template,
        listing_view_templates=listing_view_templates,
        contacts_view_templates=contacts_view_templates,
        listing_about_templates=listing_about_templates,
        email=flask.session[util.SESS_EMAIL],
        base_url=config['BASE_URL'],
        **temp_vals
    )


@blueprint.route('/categories.json')
@util.require_login()
def get_categories():
    tags = services.listing_service.index_tags()
    return json.dumps(services.listing_service.collect_index_dict(
        tags,
        home_only=False
    ))


def is_admin():
    return util.check_admin_requirement(True)


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


@blueprint.route('/content/<type>', methods=['PUT', 'POST'])
@util.require_login()
def update(type):
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


@blueprint.route('/content/<email>', methods=['DELETE'])
@util.require_login()
def delete(email):
    """Delete a listing through the JSON-REST API.

    @return: JSON-encoded document describing the deleted listing.
    @rtype: str
    """
    listing = services.listing_service.read_by_email(email)

    if not is_admin():
        flask.abort(403)

    services.listing_service.delete(listing)

    result_dict = listing
    return json.dumps(result_dict, default=json_util.default)
