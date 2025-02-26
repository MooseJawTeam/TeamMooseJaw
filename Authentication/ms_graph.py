import requests
import msal
from django.conf import settings

GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

def get_msal_app():
    """Return a configured MSAL confidential client app"""
    return msal.ConfidentialClientApplication(
        settings.MICROSOFT_AUTH['CLIENT_ID'],
        authority=settings.MICROSOFT_AUTH['AUTHORITY'],
        client_credential=settings.MICROSOFT_AUTH['CLIENT_SECRET']
    )

def get_access_token():
    """Obtain an access token from Microsoft Graph API"""
    msal_app = get_msal_app()
    result = msal_app.acquire_token_for_client(scopes=settings.MICROSOFT_AUTH['SCOPES'])

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Could not obtain access token", result)

def get_user_info(access_token):
    """Fetch user profile data using Microsoft Graph API"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{GRAPH_API_URL}/me", headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None
