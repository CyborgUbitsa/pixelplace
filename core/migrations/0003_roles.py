from django.db import migrations

def create_groups(apps, schema_editor):
    Group        = apps.get_model("auth", "Group")
    Permission   = apps.get_model("auth", "Permission")
    content_type = apps.get_model("contenttypes", "ContentType")

    artist  = Group.objects.get_or_create(name="artist")[0]
    mod     = Group.objects.get_or_create(name="moderator")[0]
    admin_g = Group.objects.get_or_create(name="admin")[0]

    pixel_ct = content_type.objects.get(app_label="core", model="pixelchange")
    view_log = Permission.objects.get(content_type=pixel_ct, codename="view_pixelchange")
    mod.permissions.add(view_log)

    canvas_ct = content_type.objects.get(app_label="core", model="canvas")
    perms = Permission.objects.filter(content_type=canvas_ct, codename__in=["add_canvas", "delete_canvas"])
    admin_g.permissions.set(perms)

    admin_g.save(); mod.save(); artist.save()

class Migration(migrations.Migration):
    dependencies = [("core", "0002_canvastile")]
    operations = [migrations.RunPython(create_groups)]
