
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def grant_suspension_permission(sender, **kwargs):
    ct = ContentType.objects.get(app_label="core", model="usersuspension")
    perm = Permission.objects.get(content_type=ct, codename="view_usersuspension")
    group, _ = Group.objects.get_or_create(name="moderator")
    group.permissions.add(perm)