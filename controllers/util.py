"""Utility functions for controllers.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
from functools import wraps

import flask

SESS_EMAIL = 'auth_user'
SESS_IS_ADMIN = 'is_admin'
SESS_PASSWORD = 'password'
SESS_VALIDATION_ERROR = 'validation error'
SESS_CONFIRMATION_MSG = 'confirmation message'
SESS_VALIDATION_SHOW_RESET = 'show reset'

AUTH_STRATEGIES = {}

def check_active_requirement_inner():
    """Check if the current user meets the requirement to be logged in.

    @return: True if the user meets the requirement, False if not
    @rtype: bool
    """
    return flask.session.get(SESS_EMAIL, None) != None

AUTH_STRATEGIES['check_active_requirement'] = check_active_requirement_inner


def check_admin_requirement_inner(admin_required):
    """Check if the current user meets the requirement to be an admin.

    @param admin_required: Whether or not the user is required to be an admin
    @type admin_required: bool
    @return: True if the user meets the requirement, False if not
    @rtype: bool
    """
    if not admin_required:
        return True
    return flask.session.get(SESS_IS_ADMIN, False)

AUTH_STRATEGIES['check_admin_requirement'] = check_admin_requirement_inner


def inject_auth_strategy(name, function):
    AUTH_STRATEGIES[name] = function


def check_active_requirement():
    return AUTH_STRATEGIES['check_active_requirement']()


def check_admin_requirement(admin_required):
    return AUTH_STRATEGIES['check_admin_requirement'](admin_required)


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


def remove_element_by_id(items, item_id, idAttribute='_id'):
    """Remove a dict element from a list for a given id.

    @param items: The list to remove an item from.
    @type items: iterable over dict
    @param item_id: The id of the item to remove from the items list.
    @type item_id: str or int
    @param idAttribute: The key of the id field of each item.
    @type idAttribute: str
    @return: True if success and item has been removed, False if unsuccessful
        and the item not removed.
    @rtype: bool
    """
    items_len = len(items)
    items[:] = [item for item in items if item.get(idAttribute) != item_id]
    if len(items) != items_len - 1:
        return False
    return True



def prepare_subcategory(listing_url_base, category, subcategory):
    """Preprare a subcategory for a view by calculating its URL.

    @param listing_url_base: The base url.
    @type listing_url_base: str
    @param category: The URL-safe category the subcategory belongs to.
    @type category: str
    @param subcategory: The view-appropriate subcategory name.
    @type subcategory: str
    @return: subcategory url and subcategory name
    @rtype: dict
    """
    return {
        'url': '/'.join((listing_url_base, category, subcategory)),
        'name': subcategory
    }

# def after_this_request(func):
#     """Performs a task/function after returning a response.

#     Calls a given functions after the controller routing function returns.

#     @param func: The function to perform.
#     @type func: function
#     """
#     if not hasattr(flask.g, 'call_after_request'):
#         flask.g.call_after_request = []
#     flask.g.call_after_request.append(func)
#     return func
