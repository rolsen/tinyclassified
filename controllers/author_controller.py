"""Controllers for handling each author's CRUD functionality for listings.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import json

import flask

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
    return flask.render_template('author/controls.html')


@blueprint.route('/create', methods=['POST'])
@util.require_login()
def create_listing():
    listing = json.loads(flask.request.form['listing'])
    services.listing_service.create(listing)
    return json.dumps(listing)


@blueprint.route('/show/<path:listing_slug>')
@util.require_login()
def show_listing(listing_slug):
    listings = services.listing_service.list_by_slug(listing_slug)
    if not listings:
        return '', 404

    return json.dumps(listings)


@blueprint.route('/update/<path:listing_slug>', methods=['PUT'])
@util.require_login()
def update_listing(listing_slug):
    listing = json.loads(flask.request.form['listing'])
    try:
        services.listing_service.update(listing_slug, listing)
    except ValueError:
        return '', 404

    return json.dumps(listing)


@blueprint.route('/delete/<path:listing_slug>', methods=['POST'])
@util.require_login()
def delete_listing(listing_slug):
    try:
        services.listing_service.delete_by_slug(listing_slug)
    except ValueError:
        return '', 404

    return ''
