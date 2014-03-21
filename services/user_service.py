"""Service for user CRUD.

@author: Rory Olsen (rolsen, Gleap LLC 2014)
@license: GNU GPLv3
"""
import tiny_classified

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
