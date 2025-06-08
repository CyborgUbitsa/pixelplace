from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Canvas(models.Model):
    name = models.CharField(max_length=100)
    width = models.PositiveIntegerField(default=2000)
    height = models.PositiveIntegerField(default=2000)
    created_at = models.DateTimeField(auto_now_add=True)

class PixelChange(models.Model):
    canvas = models.ForeignKey(Canvas, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    x = models.PositiveIntegerField()
    y = models.PositiveIntegerField()
    color = models.PositiveIntegerField()           # packed RGB
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    meta = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
