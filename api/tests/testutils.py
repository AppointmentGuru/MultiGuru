from django.contrib.auth import get_user_model
from ..models import *

def create_fake_user(username):
    return get_user_model().objects.create_user(username=username, password='testtest')

def create_fake_group(name, owners=[], members=[], permissions=[]):
    group = Group.objects.create(
        name=name,
        code=name,
        owners=owners,
        members=members
    )

    for perm in permissions:
        Permission.objects.create(
            group=group,
            code=perm,
            name=perm)

    group.refresh_from_db()
    return group
