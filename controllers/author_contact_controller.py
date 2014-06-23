"""Controllers for handling each author's CRUD functionality for contacts.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import json

import flask

try:
    from tinyclassified import tiny_classified
    from tinyclassified import services
except:
    import tiny_classified
    import services

import util

# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'author_contact',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)


@blueprint.route('/content/<author_email>/contact', methods=['POST'])
@util.require_login()
def create(author_email):
    """Creates a new listing contact through the JSON-REST API.

    @param author_email: The email address that the listing belongs to.
    @type author_email: str
    @return: JSON-encoded document describing the contact just created.
    @rtype: str
    """
    model = json.loads(flask.request.form.get('model'))
    contact_type = model.get('type')
    value = model.get('value')

    listing = services.listing_service.read_by_email(author_email)
    if not listing:
        listing = services.listing_service.create_default_listing_for_user(
            author_email
        )

    if not listing.get('contact_infos', None):
        listing['contact_infos'] = []
        listing['contact_id_next'] = 0

    if not listing.get('contact_id_next'):
        contacts = listing['contact_infos']
        if len(contacts) == 0:
            listing['contact_id_next'] = 0
        else:
            listing['contact_id_next'] = max(
                map(lambda x: x['_id'], )
            ) + 1

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


@blueprint.route('/content/<author_email>/contact/<int:contact_id>', methods=['GET'])
@util.require_login()
def read(author_email, contact_id):
    """Get information on a contact listing through the JSON-REST API.

    @param author_email: The email address that the listing belongs to.
    @type author_email: str
    @param contact_id: The integer ID of the contact record to read.
    @type contact_id: str or int
    @return: JSON-encoded document describing the requested contact.
    @rtype: str
    """
    listing = services.listing_service.read_by_email(author_email)
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


@blueprint.route('/content/<author_email>/contact', methods=['GET'])
@util.require_login()
def index(author_email):
    """Get the listing contacts for an author through the JSON-REST API.

    @param author_email: The email address that the listing belongs to.
    @type author_email: str
    @return: JSON-encoded document describing the requested contact infos.
    @rtype: str
    """
    listing = services.listing_service.read_by_email(author_email)

    if not listing:
        return 'Listing not found for author.', 404

    return json.dumps(listing.get('contact_infos', None))


@blueprint.route('/content/<author_email>/contact/<int:contact_id>', methods=['DELETE'])
@util.require_login()
def delete(author_email, contact_id):
    """Delete a listing contact through the JSON-REST API.

    @param author_email: The email address that the listing belongs to.
    @type author_email: str
    @param contact_id: The integer ID of the contact record to delete.
    @type contact_id: str or int
    @return: Confirmation message that the listing contact was deleted
        with status code 200.
    @rtype: tuple (str, int)
    """
    # TODO: Put db operations in util.after_this_request
    listing = services.listing_service.read_by_email(author_email)
    contacts = listing.get('contact_infos', None)
    if not contacts:
        return 'Contact not found', 404

    success = util.remove_element_by_id(contacts, contact_id)
    if not success:
        return 'Contact not found', 404

    listing['contact_infos'] = contacts
    services.listing_service.update(listing)

    return 'Contact deleted.', 200
