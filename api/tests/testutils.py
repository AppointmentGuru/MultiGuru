from django.contrib.auth import get_user_model
from django.conf import settings
from ..models import *
from faker import Factory

import responses

FAKE = Factory.create()

def add_response(path='/api/clients/', response_data={}, status=200):

    url = '{}{}'.format(settings.APPOINTMENTGURU_URL, path)
    responses.add(
        responses.GET,
        url,
        json=response_data,
        status=status)

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

def create_fake_group_and_members(name, num_members=3, permissions=[]):
    owner = create_fake_user(FAKE.user_name())
    members = [owner.id]
    for x in range(0, num_members):
        member = create_fake_user(FAKE.user_name())
        members.append(member.id)
    group = create_fake_group(name, owners=[owner.id], members=members)
    return (group, owner)