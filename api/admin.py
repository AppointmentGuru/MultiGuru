from django.contrib import admin
from api.models import (Group, Permission)

admin.site.register(Group)
admin.site.register(Permission)