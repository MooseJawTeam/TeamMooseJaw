import os
import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moosejawums.settings")
django.setup()

# Import User model
from ums.models import Users
from django.contrib.sessions.backends.db import SessionStore

# Get or create test user
user, created = Users.objects.get_or_create(
    id='test123',
    defaults={
        'name': 'Test User',
        'email': 'test@example.com',
        'role': 'Admin',
        'status': 'Active'
    }
)
print(f"Creating session for user: {user.name}")

# Create a new session
session = SessionStore()
session['user_id'] = user.id
session['user_name'] = user.name
session['user_email'] = user.email
session['user_role'] = user.role
session['is_authenticated'] = True
session.create()

print(f"Session created with key: {session.session_key}")
print(f"To use this session, add the following cookie to your browser:")
print(f"sessionid={session.session_key}")

print("\nHere's the full session data:")
print(session.items())