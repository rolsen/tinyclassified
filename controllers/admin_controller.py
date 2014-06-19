"""Controllers / Flack request handlers for handling admin access.

Controllers / Flask request handlers that handle application-wide admin
functionality, such as approving / denying listings, managing listings, setting
application settings, and view application stats.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask

from .. import services

# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'admin',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)


@blueprint.route('/pending')
def index_pending_listings():
    """List all listings that are pending approval and the associated controls.

    @return: HTML with the pending listings and associated controls.
    @rtype: str
    """
    raise NotImplementedError


@blueprint.route('/pending/<int:listing_id>')
def show_pending_listing(listing_id):
    """Show details about a pending listing.

    @param listing_id: The id of listing to show
    @type listing_id: int
    @return: HTML with the listing details
    @rtype: str
    """
    raise NotImplementedError


@blueprint.route('/approve/<int:listing_id>', methods=['PUT'])
def approve_pending_listing(listing_id):
    """Approves a pending listing.

    @param listing_id: The id of pending listing to approve
    @type listing_id: int
    @return: Redirect to the pending listings index
    @rtype: flask.redirect
    """
    raise NotImplementedError


@blueprint.route('/deny/<int:listing_id>', methods=['PUT'])
def deny_pending_listing(listing_id):
    """Denys a pending listing and notifies the listing owner why.

    @param listing_id: The id of pending listing to deny
    @type listing_id: int
    @return: Redirect to the pending listings index
    @rtype: flask.redirect
    """
    raise NotImplementedError


@blueprint.route('/manage')
def index_manage_listings():
    """List all previously approved listings and the controls to manage them.

    @return: HTML with the listings and associated controls.
    @rtype: str
    """
    raise NotImplementedError


@blueprint.route('/manage/<int:listing_id>')
def show_manage_listing(listing_id):
    """Show details about a listing from an admin perspective.

    @param listing_id: The id of listing to show
    @type listing_id: int
    @return: HTML with the listing details
    @rtype: str
    """
    raise NotImplementedError


@blueprint.route('/delete/<int:listing_id>', methods=['PUT'])
def delete_listing(listing_id):
    """Delete a listing and notify the listing owner why.

    @param listing_id: The id of listing to delete
    @type listing_id: int
    @return: Redirect to the manage listings index
    @rtype: flask.redirect
    """
    raise NotImplementedError


@blueprint.route('/settings')
def index_settings():
    raise NotImplementedError


# Client-side sends array of changed values in flask.request.form
@blueprint.route('/update_settings', methods=['PUT'])
def update_settings():
    raise NotImplementedError


@blueprint.route('/stats')
def index_stats():
    raise NotImplementedError
