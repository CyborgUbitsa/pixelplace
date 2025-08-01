from django.contrib import admin
from django.urls import path, reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.urls import path, include
from core import views as core_views 
from core.views import CustomLoginView

urlpatterns = [
    path("", core_views.home, name="home"),

    path("canvas/<int:canvas_id>/",           core_views.canvas_view,  name="canvas"),
    path("api/canvas/<int:canvas_id>/snapshot/png/", core_views.snapshot_png, name="snap_png"),
    path("canvas/<int:canvas_id>/log/",       core_views.audit_log,    name="audit_log"),


    path("signup/", core_views.signup, name="signup"),


    path(
        "login/",
        CustomLoginView.as_view(
            next_page=reverse_lazy("home")
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page=reverse_lazy("home"),
        ),
        name="logout",
    ),

    path("admin/", admin.site.urls),
    path(
    "canvas/<int:canvas_id>/subscribe/",
    core_views.subscribe_canvas,
    name="subscribe_canvas",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
    path("suspended/", core_views.suspended_view, name="suspended"),
]

def redirect_404(request, exception):
    return redirect("home")

handler404 = "pixelplace.urls.redirect_404"
