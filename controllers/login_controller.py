"""Controllers / Flask request handlers for handling user authentication.

Controllers / Flask request handlers that handle user logins, logouts, and
forgotten password requests. These endpoints are not RESTful.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import flask
import werkzeug
from werkzeug import security

try:
    from tinyclassified import tiny_classified
    from tinyclassified import services
except:
    import tiny_classified
    import services

import util

PASSWORD_RESET_MESSAGE = 'Password reset. Please check your email inbox.'

USER_LOGIN_FAIL_MESSAGE = 'Sorry! Either your username or password is '\
    'incorrect. Please try again.'
USER_PASSWORD_INVALID_MSG = USER_LOGIN_FAIL_MESSAGE
USER_NOT_FOUND_MSG = USER_LOGIN_FAIL_MESSAGE
CONFIRM_PASSWORD_MISMATCH_MSG = 'Whoops! Your new password and confirm new '\
    'password inputs were different. Please try again.'
USER_PASSWORD_CHANGED_MSG = 'Password updated!'


# Create a Flask blueprint to split the Flask routes amoung multiple files.
blueprint = flask.Blueprint(
    'login',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)


@blueprint.route('/login', methods=['GET'])
def login():
    """Render the login view with login form.

    @return: The HTML login view.
    @rtype: str
    """
    flask.session[util.SESS_EMAIL] = None
    flask.session[util.SESS_IS_ADMIN] = None

    error = flask.session.get(util.SESS_VALIDATION_ERROR, None)
    if error:
        del flask.session[util.SESS_VALIDATION_ERROR]

    show_reset_password = flask.session.get(
        util.SESS_VALIDATION_SHOW_RESET, None)
    if show_reset_password:
        del flask.session[util.SESS_VALIDATION_SHOW_RESET]

    confirm = flask.session.get(util.SESS_CONFIRMATION_MSG, None)
    if confirm:
        del flask.session[util.SESS_CONFIRMATION_MSG]

    config = tiny_classified.get_config()

    temp_vals = tiny_classified.render_common_template_vals()

    return flask.render_template(
        'login/login.html',
        error=error,
        confirm=confirm,
        show_reset_password=show_reset_password,
        base_url=config['BASE_URL'],
        parent_template=config.get('PARENT_TEMPLATE', 'base.html'),
        **temp_vals
    )


@blueprint.route('/login', methods=['POST'])
def login_post():
    """Handle user login form POSTs.

    @return: Redirect to author chrome if login successful otherwise redirect
        back to the login form with validation error.
    @rtype: flask.redirect
    """
    email = flask.request.form[util.SESS_EMAIL].lower()
    challenge_password = flask.request.form[util.SESS_PASSWORD]

    # Find user
    user = services.user_service.read(email)
    if not user:
        flask.session[util.SESS_VALIDATION_ERROR] = USER_NOT_FOUND_MSG
        flask.session[util.SESS_VALIDATION_SHOW_RESET] = True
        return flask.redirect(flask.url_for('login.login'))

    # Check password
    phash = user['password_hash']
    password_correct = phash != None and werkzeug.security.check_password_hash(
        phash,
        challenge_password
    )
    if not password_correct:
        flask.session[util.SESS_VALIDATION_ERROR] = USER_PASSWORD_INVALID_MSG
        flask.session[util.SESS_VALIDATION_SHOW_RESET] = True
        return flask.redirect(flask.url_for('login.login'))

    # Start session
    flask.session[util.SESS_EMAIL] = user['email']
    flask.session[util.SESS_IS_ADMIN] = user['is_admin']
    destination_url = flask.url_for('author.show_user_ui')
    return flask.redirect(destination_url)


@blueprint.route('/logout')
def logout():
    """Handle user logouts.

    @return: Redirect to login form with session credentials reset to None.
    @rtype: flask.redirect
    """
    flask.session[util.SESS_EMAIL] = None
    flask.session[util.SESS_IS_ADMIN] = None
    return flask.redirect(flask.url_for('login.login'))


@blueprint.route('/forgot_password', methods=['GET'])
def forgot_password():
    """Render the forgot password view with forgot password form.

    @return: The HTML forgot password view.
    @rtype: str
    """
    config = tiny_classified.get_config()
    return flask.render_template(
        'login/forgot_password.html',
        base_url=config['BASE_URL'],
        parent_template=config.get('PARENT_TEMPLATE', 'base.html')
    )


@blueprint.route('/forgot_password', methods=['POST'])
def forgot_password_post():
    """Handle user forgot password POSTs.

    @return: Redirect to the login form with a confirmation message.
    @rtype: flask.redirect
    """
    email = flask.request.form[util.SESS_EMAIL].lower()
    user = services.user_service.read(email)
    if not user:
        flask.session[util.SESS_CONFIRMATION_MSG] = PASSWORD_RESET_MESSAGE
        return flask.redirect(flask.url_for('login.login'))

    new_password = services.user_service.generate_password()
    services.user_service.update_password(user, new_password, True, True)

    flask.session[util.SESS_CONFIRMATION_MSG] = PASSWORD_RESET_MESSAGE
    return flask.redirect(flask.url_for('login.login'))
