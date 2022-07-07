from django.urls import path, re_path

from . import views
from .api_views import api

app_name = "network"

react_routes = ["profile", "following"]

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("api/", api.urls),
    # re_path(r"^.*", views.index, name="react_root"),
    re_path(rf"{('|').join(react_routes)}", views.index, name="react_root"),
]
