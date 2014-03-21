"""Utility functions for controllers.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
from functools import wraps

import flask

SESS_EMAIL = 'email'
SESS_IS_ADMIN = 'is_admin'


def check_active_requirement():
    """Check if the current user meets the requirement to be logged in.

    @return: True if the user meets the requirement, False if not
    @rtype: bool
    """
    return flask.session.get(SESS_EMAIL, None) != None


def check_admin_requirement(admin_required):
    """Check if the current user meets the requirement to be an admin.

    @param admin_required: Whether or not the user is required to be an admin
    @type admin_required: bool
    @return: True if the user meets the requirement, False if not
    @rtype: bool
    """
    if not admin_required:
        return True
    return flask.session.get(SESS_IS_ADMIN, False)


def redirect_inactive_user():
    return flask.redirect(
        flask.url_for('login.login', next=flask.request.url)
    )

def redirect_unauthorized_user():
    return redirect_inactive_user()


def require_login(admin=False):
    """Decorate a view to require certain account credentials.

    Decorates a view function to require certain account credentials,
    redirecting to the login page if the current user does not have the
    required credentials.

    @param f: The view function to decorate.
    @type f: function
    @keyword admin: If true require the user to be an administrator or to have
        "admin" status.
    @type team: bool
    @return: Decorated function
    @rtype: function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_active_requirement():
                return redirect_inactive_user()

            if not check_admin_requirement(admin):
                return redirect_unauthorized_user()

            return f(*args, **kwargs)
        return decorated_function
    return decorator
