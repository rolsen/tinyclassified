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

# Load configuration settings
app.config.from_pyfile('flask_config.cfg', silent=False)

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
        controllers.login_controller.blueprint,
        url_prefix='/login'
    )

@app.route('/health')
def show_health_report():
    return 'TODO: More health info. Anyway, server active.'

attach_blueprints()

def get_db_adapter():
    return db_adapter

if __name__ == '__main__':
    app.config['DEBUG'] = True
    mongo = PyMongo(app)
    db_adapter = services.db_service.DBAdapter(app)
    app.run()
