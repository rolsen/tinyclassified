"""Controllers / Flask request handlers for handling user authentication.

Controllers / Flask request handlers that handle user logins, logouts, and
forgotten password requests. These enpoints are not RESTful.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask
# import os
# import werkzeug
# from werkzeug import security

# import models
# import services

# import controller_constant
# import util


# PASSWORD_RESET_MESSAGE = 'Password reset. Please check your email inbox.'

# USER_LOGIN_FAIL_MESSAGE = 'Sorry! Either your username or password is '\
#     'incorrect. Please try again.'
# USER_PASSWORD_INVALID_MSG = USER_LOGIN_FAIL_MESSAGE
# USER_NOT_FOUND_MSG = USER_LOGIN_FAIL_MESSAGE
# CONFIRM_PASSWORD_MISMATCH_MSG = 'Whoops! Your new password and confirm new '\
#     'password inputs were different. Please try again.'
# USER_PASSWORD_CHANGED_MSG = 'Password updated!'


# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'login',
    __name__,
    template_folder='templates'
)

@blueprint.route('/', methods=['GET'])
def login():
    return flask.render_template('login/login.html')
