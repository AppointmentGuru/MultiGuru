from django.contrib import admin
from api.models import (Group, Permission, Hub)

admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(Hub)