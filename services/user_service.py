"""Service for user CRUD.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import random
import string

import werkzeug

import tiny_classified

import email_service

PASSWORD_LENGTH = 12

PASSWORD_EMAIL_SUBJECT = 'TinyClassified password updated.'

NEW_PASSWORD_EMAIL_WITH_PASS = '''Hello!

You or someone pretending to be you just changed your password for
TinyClassified to **%s**. If this wasn't you, please let the site administrator
know.

Thanks,
The robots at TinyClassified
'''

NEW_PASSWORD_EMAIL_WITHOUT_PASS = '''Hello!

You or someone pretending to be you just changed your password for
TinyClassified. If this wasn't you, please let the site administrator know.

Thanks,
The robots at TinyClassified
'''

def create(user):
    """Create a new user.

    @param user: The user to create.
    @type user: dict
    @raises: ValueError if the given user describes a email address that already
        exists.
    """
    if read(user['email']):
        raise ValueError('A user with that email address already exists.')

    tiny_classified.get_db_adapter().upsert_user(user)


def read(email):
    """Get the user that corresponds to the given email address.

    @param email: The email of the user to find.
    @type email: str
    @return: The user or None
    @rtype: dict or None
    """
    return tiny_classified.get_db_adapter().get_user_by_email(email)


def update(original_email, user):
    """Updates / modifies a user by their previous email address.

    @param original_email: The previous / current email of the user to update.
    @type original_email: str
    @param user: The updated user
    @type user: dict
    @raises: ValueError if the given email address does not correspond to a user
    """
    original_user = read(original_email)

    if not original_user:
        raise ValueError('A user with that email address does not exist.')

    user['_id'] = original_user['_id']

    tiny_classified.get_db_adapter().upsert_user(user)


def delete(user):
    """Delete / remove a user.

    @param user: The user or user email to delete
    @type user: dict or str
    """
    if isinstance(user, basestring): email = user
    else: email = user['email']

    tiny_classified.get_db_adapter().delete_user(email)


def generate_password():
    """Generate a random password.

    @return: The randomly generated password.
    @rtype: str
    """
    chars = string.ascii_letters + string.digits + '!@#$^*()'
    return ''.join(random.choice(chars) for i in range(PASSWORD_LENGTH))


def update_password(user, password, send_email=True,
    include_password_in_email=True):
    """Update a user's password and optionally send an email with password.

    @param user: The user hash.
    @type email_or_user: dict
    @param password: User's new plain text password
    @type password: str
    @param include_password_in_email: Flag indicating if the new password should
        be sent with the email notification about the password change.
    @type include_password_in_email: bool
    """
    pass_hash = werkzeug.generate_password_hash(password, method='sha512')
    user['password_hash'] = pass_hash
    update(user['email'], user)

    if include_password_in_email:
        plaintext_message = NEW_PASSWORD_EMAIL_WITH_PASS % password
    else:
        plaintext_message = NEW_PASSWORD_EMAIL_WITHOUT_PASS

    if send_email:
        email_service.send(
            [user['email']],
            PASSWORD_EMAIL_SUBJECT,
            plaintext_message
        )
