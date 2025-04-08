from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Check if user is logged in
            if 'user_id' not in request.session:
                messages.error(request, "Please log in to access this page.")
                return redirect('index')
                
            # Check if session has expired
            if not request.session.get('is_authenticated'):
                messages.error(request, "Your session has expired. Please log in again.")
                return redirect('index')
                
            # Check role permissions
            session_role = request.session.get('user_role', '').lower()
            allowed_roles_lower = [role.lower() for role in allowed_roles]

            if session_role not in allowed_roles_lower:
                messages.error(request, "You do not have permission to access this page.")
                return redirect('index')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator