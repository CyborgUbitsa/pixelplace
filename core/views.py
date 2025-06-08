from django.http import HttpResponse 
from django.shortcuts import get_object_or_404, render
from PIL import Image
import zlib

from .models import Canvas, CanvasTile, TILE_SIZE

def canvas_view(request, canvas_id: int):
    canvas = get_object_or_404(Canvas, pk=canvas_id)
    return render(
        request,
        "core/canvas.html",
        {
            "canvas": canvas,
            "ws_url": f"ws://{request.get_host()}/ws/canvas/{canvas_id}/",
        },
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
