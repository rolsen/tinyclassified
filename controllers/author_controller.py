"""Controllers for handling each author's CRUD functionality for listings.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import json

import flask

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

    return flask.render_template(
        'author/author_chrome.html',
        listing_view_templates=listing_view_templates,
        contacts_view_templates=contacts_view_templates,
        email=flask.session[util.SESS_EMAIL],
        base_url=tiny_classified.get_config()['BASE_URL']
    )
