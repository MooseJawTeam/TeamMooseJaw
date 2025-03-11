from django.shortcuts import redirect
from functools import wraps

from django.shortcuts import redirect
from functools import wraps
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def role_required(allowed_roles=[]):
    """
    Decorator to restrict access based on user roles.
    Usage: @role_required(["Admin"])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.session.get("user_role")

            if not user_role:
                logger.warning(f"Unauthorized access attempt: No role found in session.")
                return redirect("welcome")

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)

            logger.warning(f"Unauthorized access attempt by user with role '{user_role}'")
            return redirect("welcome")

        return wrapper
    return decorator
