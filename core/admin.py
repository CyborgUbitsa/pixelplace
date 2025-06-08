from django.contrib import admin
from .models import Canvas, PixelChange, AuditLog


@admin.register(Canvas)
class CanvasAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "width", "height", "created_at")
    search_fields = ("name",)


@admin.register(PixelChange)
class PixelChangeAdmin(admin.ModelAdmin):
    list_display = ("id", "canvas", "user", "x", "y", "color", "created_at")
    list_filter = ("canvas", "user")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "created_at")
    search_fields = ("action",)
