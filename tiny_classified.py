"""Main entry point for the TinyClassified software.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask
import flask_sslify
from flask.ext.pymongo import PyMongo

import controllers
import services

# Create application
app = flask.Flask(__name__)
sslify = flask_sslify.SSLify(app)

app.config.from_pyfile('flask_config.cfg', silent=False)

db_adapter = services.db_service.DBAdapter(app)

# Load configuration settings
app.config.from_pyfile('flask_config.cfg', silent=False)

def setup_template_functions():
    app.jinja_env.globals.update(get_slug=services.listing_service.get_slug)

def attach_blueprints():
    app.register_blueprint(
        controllers.public_controller.blueprint,
        url_prefix='/public'
    )
    app.register_blueprint(
        controllers.admin_controller.blueprint,
        url_prefix='/admin'
    )
    app.register_blueprint(
        controllers.author_controller.blueprint,
        url_prefix='/author'
    )
    app.register_blueprint(
        controllers.author_contact_controller.blueprint,
        url_prefix='/author'
    )
    app.register_blueprint(
        controllers.login_controller.blueprint
    )

@app.route('/health')
def show_health_report():
    return 'TODO: More health info. Anyway, server active.'

@app.after_request
def per_request_callbacks(response):
    for func in getattr(flask.g, 'call_after_request', ()):
        response = func(response)
    return response

def get_db_adapter():
    return db_adapter

def get_config():
    return app.config

if __name__ == '__main__':
    app.config['DEBUG'] = True
    attach_blueprints()
    setup_template_functions()
    mongo = PyMongo(app)
    app.run()
