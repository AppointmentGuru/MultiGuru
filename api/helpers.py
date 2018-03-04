from .models import Group
import requests, os

def can_become(user, sudo, required_permission=None, group=None):
    '''
    If both users are members of the same group,
    then this user has permission to become the other user
    '''

    groups = Group.objects.filter(members__contains=[sudo])
    for group in groups:
        if user in group.members:
            return True
    return False

def group_can_become(group, user, sudo, requested_permission):
    '''Slightly simpler than can_become because we provide the group'''
    # find shared groups:
    try:
        group = Group.objects.get(
            id=group,
            members__contains=[user, sudo])
        return True
    except group.DoesNotExist:
        return False

def kong_login(user_id):
    data = {
        "client_id": os.environ.get('KONG_CLIENT_ID'),
        "client_secret": os.environ.get('KONG_CLIENT_SECRET'),
        "grant_type": "password",
        "provision_key": os.environ.get('KONG_PROVISION_KEY'),
        "authenticated_userid": user_id,
    }
    oauth_base_url = os.environ.get('KONG_OAUTH_BASE_URL')
    url = '{}/oauth2/token/'.format(oauth_base_url)
    return requests.post(url, data).json()
