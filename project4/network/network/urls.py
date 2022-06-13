from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path

from . import views
from .api_views import api

app_name = "network"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile", views.index, name="profile"),
    path("following", views.index, name="following"),
    path("api/", api.urls),
    re_path(r"^.*", views.index, name="react_root"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
