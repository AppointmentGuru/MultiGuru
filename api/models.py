from django.db import models
from django.contrib.postgres.fields import ArrayField

POSSIBLE_PERMISSIONS = (
    ('can_view_slots', 'Can view available slots in your calendar',),
    ('can_view_calendar', 'Can view your calendar',),
    ('can_create_appointment', 'Can create appointments on your calendar',),
    ('full_access', 'Full access to your account',),
)

class Group(models.Model):
    '''
    e.g.: Some Practice, or "Referrers"
    '''

    def __str__(self):
        return self.name

    owners = ArrayField(models.CharField(max_length=36), default=[])
    members = ArrayField(models.CharField(max_length=36), default=[])

    code = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

class Permission(models.Model):
    '''
    Permissions can be added to a group and determine what sort of things members of that group can get up to
    '''
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    code = models.CharField(max_length=100, choices=POSSIBLE_PERMISSIONS)
    name = models.CharField(max_length=255)



