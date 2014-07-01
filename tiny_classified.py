"""Main entry point for the TinyClassified software.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask
#import flask_sslify
from flask.ext.pymongo import PyMongo

import config_cache


def setup_template_functions(target):
    """Attach template functions to an app.

    @param target: The Flask app to attach TinyClassified blueprints to.
    @type target: flask.app.Flask
    """
    import services
    target.jinja_env.globals.update(get_slug=services.listing_service.get_slug)

def attach_blueprints(target):
    """Attach Flask blueprints to an app.

    @param target: The Flask app to attach TinyClassified blueprints to.
    @type target: flask.app.Flask
    """
    import controllers
    base_url_prefix = get_config()['BLUEPRINT_BASE_URL']

    target.register_blueprint(
        controllers.public_controller.blueprint,
        url_prefix= base_url_prefix
    )
    target.register_blueprint(
        controllers.admin_controller.blueprint,
        url_prefix= base_url_prefix + '/admin'
    )
    target.register_blueprint(
        controllers.author_controller.blueprint,
        url_prefix= base_url_prefix + '/author'
    )
    target.register_blueprint(
        controllers.author_contact_controller.blueprint,
        url_prefix= base_url_prefix + '/author'
    )
    target.register_blueprint(
        controllers.login_controller.blueprint
    )

#@app.route('/health')
#def show_health_report():
#    return 'TODO: More health info. Anyway, server active.'
#
#@app.after_request
#def per_request_callbacks(response):
#    for func in getattr(flask.g, 'call_after_request', ()):
#        response = func(response)
#    return response

def get_db_adapter():
    config = config_cache.get_config()
    if not config['db_adapter']:
        import services
        config['db_adapter'] = services.db_service.DBAdapter()
    return config['db_adapter']

def set_db_adapter(new_adapter):
    config_cache.get_config()['db_adapter'] = new_adapter

def set_overwrite_config(config):
    config_cache.get_config()['config'] = config


def get_config():
    return config_cache.get_config()['config']


def set_app(app):
    config_cache.get_config()['app'] = app

def get_app():
    return config_cache.get_config()['app']


def initialize_standalone():
    # Create application
    app = flask.Flask(__name__)
    #sslify = flask_sslify.SSLify(app)

    app.config.from_pyfile('flask_config.cfg', silent=False)

    set_overwrite_config(app.config)

    set_app(app)

    attach_blueprints(app)
    setup_template_functions(app)


def set_render_common_template_vals(func):
    config_cache.get_config()['get_common_template_vals'] = func


def render_common_template_vals(slug):
    return config_cache.get_config()['get_common_template_vals'](slug)


if __name__ == '__main__':
    initialize_standalone()

    app = get_app()
    app.config['DEBUG'] = True
    app.run()
