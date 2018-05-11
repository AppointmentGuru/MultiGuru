'''
Signals for Invoice model
'''
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Hub
from django.template.defaultfilters import slugify

@receiver(pre_save, sender=Hub, dispatch_uid="api.models.Hub.pre_save")
def enrich_data(sender, instance, **kwargs):
    if instance.slug is None:
        instance.slug = slugify(instance.title)
