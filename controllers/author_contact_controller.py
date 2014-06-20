"""Controllers for handling each author's CRUD functionality for contacts.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import json

import flask

import tinyclassified.tiny_classified as tiny_classified

from .. import services

import util

# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'author_contact',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)


@blueprint.route('/content/contact/<param>', methods=['POST', 'PUT'])
@util.require_login()
def create(param):
    """Creates a new listing contact through the JSON-REST API.

    @return: JSON-encoded document describing the contact just created.
    @rtype: str
    """
    email = flask.session.get(util.SESS_EMAIL, None).lower()
    model = json.loads(flask.request.form.get('model'))
    contact_type = model.get('type')
    value = model.get('value')

    listing = services.listing_service.read_by_email(email)
    if not listing:
        listing = services.listing_service.create_default_listing_for_user(email)

    if not listing.get('contact_infos', None):
        listing['contact_infos'] = []
        listing['contact_id_next'] = 0

    contact_dict = {
        'type': contact_type,
        'value': value,
        '_id': listing['contact_id_next']
    }

    # TODO: increment using mongo '$inc'
    listing['contact_id_next'] = listing['contact_id_next'] + 1
    listing['contact_infos'].append(contact_dict)

    # TODO: Put db operations in util.after_this_request
    services.listing_service.update(listing)

    return json.dumps(contact_dict)


@blueprint.route('/content/contact/<int:contact_id>', methods=['GET'])
@util.require_login()
def read(contact_id):
    """Get information on a contact listing through the JSON-REST API.

    @param contact_id: The integer ID of the contact record to read.
    @type contact_id: str or int
    @return: JSON-encoded document describing the requested contact.
    @rtype: str
    """
    email = flask.session.get(util.SESS_EMAIL, None).lower()
    listing = services.listing_service.read_by_email(email)
    contact_infos = listing.get('contact_infos', None)
    if not contact_infos:
        return 'Contact information entries not found for author.', 404

    contact_read = services.listing_service.read_contact_by_id(
        listing,
        contact_id
    )
    if not contact_read:
        return 'Contact information not found for author.', 404

    result_dict = {'contact': contact_read}
    return json.dumps(result_dict)


@blueprint.route('/content/contact', methods=['GET'])
@util.require_login()
def index():
    """Get the listing contacts for an author through the JSON-REST API.

    @return: JSON-encoded document describing the requested contact infos.
    @rtype: str
    """
    email = flask.session.get(util.SESS_EMAIL, None).lower()
    listing = services.listing_service.read_by_email(email)

    if not listing:
        return 'Listing not found for author.', 404

    return json.dumps(listing.get('contact_infos', None))


@blueprint.route('/content/contact/<int:contact_id>', methods=['DELETE'])
@util.require_login()
def delete(contact_id):
    """Delete a listing contact through the JSON-REST API.

    @param contact_id: The integer ID of the contact record to delete.
    @type contact_id: str or int
    @return: Confirmation message that the listing contact was deleted
        with status code 200.
    @rtype: tuple (str, int)
    """
    email = flask.session.get(util.SESS_EMAIL, None).lower()

    # TODO: Put db operations in util.after_this_request
    listing = services.listing_service.read_by_email(email)
    contacts = listing.get('contact_infos', None)
    if not contacts:
        return 'Contact not found', 404

    success = util.remove_element_by_id(contacts, contact_id)
    if not success:
        return 'Contact not found', 404

    listing['contact_infos'] = contacts
    services.listing_service.update(listing)

    return 'Contact deleted.', 200