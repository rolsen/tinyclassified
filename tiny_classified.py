"""Main entry point for the TinyClassified software.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask
import flask_sslify
from flask.ext.pymongo import PyMongo


OVERWRITE_CONFIG = {
    'config': None,
    'db_adapter': None,
    'get_common_template_vals': lambda: {}
}


def setup_template_functions(target):
    import services
    target.jinja_env.globals.update(get_slug=services.listing_service.get_slug)

def attach_blueprints(target):
    import controllers
    base_url_prefix = get_config()['BLUEPRINT_BASE_URL']

    print base_url_prefix

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
    if not OVERWRITE_CONFIG['db_adapter']:
        import services
        OVERWRITE_CONFIG['db_adapter'] = services.db_service.DBAdapter()
    return OVERWRITE_CONFIG['db_adapter']

def set_overwrite_config(config):
    OVERWRITE_CONFIG['config'] = config


def get_config():
    return OVERWRITE_CONFIG['config']


def initialize_standalone():
    # Create application
    app = flask.Flask(__name__)
    sslify = flask_sslify.SSLify(app)

    app.config.from_pyfile('flask_config.cfg', silent=False)
    OVERWRITE_CONFIG['config'] = app.config

    # Load configuration settings
    app.config.from_pyfile('flask_config.cfg', silent=False)


def set_render_common_template_vals(func):
    OVERWRITE_CONFIG['get_common_template_vals'] = func


def render_common_template_vals():
    return OVERWRITE_CONFIG['get_common_template_vals']()


if __name__ == '__main__':
    initialize_standalone()

    app.config['DEBUG'] = True
    attach_blueprints()
    setup_template_functions(app)
    mongo = PyMongo(app)
    app.run()
