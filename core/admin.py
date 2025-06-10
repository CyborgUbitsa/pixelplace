from django.contrib import admin
from .models import Canvas, PixelChange, AuditLog
import zlib
from io import BytesIO
from django.contrib import admin
from django.core.mail import EmailMessage
from django.utils.timezone import now
from PIL import Image
from django.contrib import admin
from django.core.mail import EmailMessage
from .models import Canvas, CanvasSubscription
from .models import Canvas, CanvasSubscription, TILE_SIZE
from .models import UserSuspension


@admin.register(PixelChange)
class PixelChangeAdmin(admin.ModelAdmin):
    list_display = ("id", "canvas", "user", "x", "y", "color", "created_at")
    list_filter = ("canvas", "user")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "action", "created_at")
    search_fields = ("action",)



@admin.register(CanvasSubscription)
class CanvasSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "canvas", "created_at")
    search_fields = ("name",)
    list_filter = ("canvas",)

@admin.register(Canvas)
class CanvasAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "width", "height")
    actions = ["email_subscribers"]

    def email_subscribers(self, request, queryset):
        for canvas in queryset:
            img = Image.new("RGB", (canvas.width, canvas.height), "white")
            tiles = canvas.canvastile_set.all()
            for tile in tiles:
                raw = zlib.decompress(tile.data)
                patch = Image.frombytes("RGB", (TILE_SIZE, TILE_SIZE), raw)
                img.paste(
                    patch,
                    (tile.tx * TILE_SIZE,
                     canvas.height - (tile.ty + 1) * TILE_SIZE)
                )
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            png_data = buffer.getvalue()
            subs = canvas.subscriptions.all()
            for sub in subs:
                subject = f"[PixelPlace] Canvas #{canvas.id} snapshot"
                body    = (
                    f"Hello!\n\n"
                    f"Here is the current state of canvas «{canvas.name}» "
                    f"as of {now().strftime('%Y-%m-%d %H:%M:%S')}.\n"
                )
                msg = EmailMessage(
                    subject=subject,
                    body=body,
                    to=[sub.email],
                )
                msg.attach(
                    f"canvas-{canvas.id}.png",
                    png_data,
                    "image/png"
                )
                msg.send(fail_silently=True)

        self.message_user(request, "Sent PNG snapshot to all subscribers")
    email_subscribers.short_description = "Email PNG to subscribers"


@admin.register(UserSuspension)
class UserSuspensionAdmin(admin.ModelAdmin):
    list_display = ("user", "start", "end", "is_active")
    list_filter  = ("user",)
    search_fields= ("user__username",)

