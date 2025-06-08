from django.db import models
from django.contrib.auth import get_user_model
import zlib, itertools
from PIL import Image   

TILE_SIZE = 64  

User = get_user_model()

class Canvas(models.Model):

    def __str__(self):
        return f"{self.name} ({self.width}x{self.height})"
    
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

def white_tile_bytes() -> bytes:
    raw = bytes([255]) * (TILE_SIZE * TILE_SIZE * 3)
    return zlib.compress(raw, level=6)

class CanvasTile(models.Model):
    canvas = models.ForeignKey("Canvas", on_delete=models.CASCADE)
    tx     = models.PositiveIntegerField()          # tile-x
    ty     = models.PositiveIntegerField()          # tile-y
    data   = models.BinaryField()                   # zlib-packed RGB
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("canvas", "tx", "ty")

    @classmethod
    def get_for_update(cls, canvas_id, tx, ty):
        try:
            return cls.objects.select_for_update().get(
                canvas_id=canvas_id, tx=tx, ty=ty
            )
        except cls.DoesNotExist:
            return cls.objects.create(
                canvas_id=canvas_id, tx=tx, ty=ty, data=white_tile_bytes()
            )
        
def snapshot_png(request, canvas_id: int):
    canvas = get_object_or_404(Canvas, pk=canvas_id)
    img = Image.new("RGB", (canvas.width, canvas.height), "white")

    for tile in CanvasTile.objects.filter(canvas_id=canvas_id):
        patch = Image.frombytes(
            "RGB", (TILE_SIZE, TILE_SIZE),
            zlib.decompress(tile.data)
        )
        img.paste(
            patch,
            (tile.tx * TILE_SIZE,
             canvas.height - TILE_SIZE - tile.ty * TILE_SIZE)
        )

    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response
