# utils/exceptions.py


class DuplicateUserError(ValueError):
    """Raised when a username (or email) is already used by another account."""


class InvalidPasswordError(ValueError):
    """Raised when a password does not respect the password policy."""


class InvalidCredentialsError(ValueError):
    """Raised when the username or the password is incorrect at login."""


class UserNotFoundError(LookupError):
    """Raised when a user does not exist."""


class NeoNotFoundError(LookupError):
    """Raised when a neo does not exist."""


class AlreadyFavoriteError(ValueError):
    """Raised when a neo is already in the favorites of the user."""
