from functools import wraps
from flask_login import current_user
from flask import abort

def role_required(role):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(403)

            if current_user.role != role:
                abort(403)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def roles_required(*roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not current_user.is_authenticated:
                abort(403)

            if current_user.role not in roles:
                abort(403)

            return func(*args, **kwargs)

        return wrapper

    return decorator
