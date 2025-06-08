from django.shortcuts import render, get_object_or_404
from .models import Canvas

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
