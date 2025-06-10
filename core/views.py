from django.http import HttpResponse 
from django.shortcuts import get_object_or_404, render
from PIL import Image
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from .models import PixelChange
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.http import HttpResponse
from PIL import Image
import io, zlib
from core.tile_utils import (
    TILE_SIZE,
    compress_tile,
    decompress_tile,
    set_pixel,
)
from django.shortcuts import render, get_object_or_404
from .models import Canvas, PixelChange
from .utils import is_moderator
from .forms import SubscriptionForm
from django.shortcuts import redirect
from .models import Canvas, CanvasTile, TILE_SIZE
from .forms import SignupForm  

def canvas_view(request, canvas_id: int):
    canvas = get_object_or_404(Canvas, pk=canvas_id)

    is_artist    = request.user.is_authenticated and \
                   request.user.groups.filter(name="artist").exists()
    is_mod       = is_moderator(request.user)
    form = SubscriptionForm()
    audit_rows = None
    if is_mod:
        audit_rows = (
            PixelChange.objects
            .filter(canvas=canvas)
            .select_related("user")
            .order_by("-id")
        )

    return render(
        request,
        "core/canvas.html",
        {
            "canvas": canvas,
            "is_artist": is_artist,
            "is_mod": is_mod,
            "audit_rows": audit_rows,
            "subscription_form": form,
        },
    )

def snapshot_png(request, canvas_id: int):
    canvas = get_object_or_404(Canvas, pk=canvas_id)

    img = Image.new("RGB", (canvas.width, canvas.height), "white")

    for tile in CanvasTile.objects.filter(canvas=canvas):
        buf = decompress_tile(tile.data)    
        tx, ty = tile.tx, tile.ty
        tile_img = Image.frombytes(
            "RGB",
            (TILE_SIZE, TILE_SIZE),
            bytes(buf),
        )
        img.paste(tile_img, (tx * TILE_SIZE, canvas.height - (ty + 1) * TILE_SIZE))

    out = io.BytesIO()
    img.save(out, "PNG", optimize=False)
    return HttpResponse(out.getvalue(), content_type="image/png")

@permission_required("core.view_pixelchange", raise_exception=True)
def audit_log(request, canvas_id: int):
    rows = PixelChange.objects.filter(canvas_id=canvas_id).select_related("user").order_by("-id")[:500]
    return render(request, "core/audit.html", {"rows": rows})

def home(request):
    canvases = Canvas.objects.all().order_by("id")
    return render(request, "core/home.html", {"canvases": canvases})

def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Group.objects.get(name="artist").user_set.add(user)
            login(request, user)
            return redirect(request.GET.get("next", "home"))
    else:
        form = SignupForm()

    return render(request, "core/signup.html", {"form": form})

def subscribe_canvas(request, canvas_id):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.canvas_id = canvas_id
            sub.save()
    return redirect("canvas", canvas_id=canvas_id)

