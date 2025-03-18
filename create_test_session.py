import os
import django
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moosejawums.settings")
django.setup()

# Import User model
from ums.models import Users

# Get test user
user = Users.objects.get(id='test123')
print(f"Creating session for user: {user.name}")

# Create a new session
session = SessionStore()
session['user_id'] = user.id
session['user_name'] = user.name
session['user_email'] = user.email
session['user_role'] = user.role
session.create()

print(f"Session created with key: {session.session_key}")
print(f"To use this session, add the following cookie to your browser:")
print(f"sessionid={session.session_key}")

print("\nHere's the full session data:")
print(session.items())