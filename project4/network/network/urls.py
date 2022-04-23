from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from . import views

app_name = "network"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("api/profile", views.profile, name="profile"),
    path("api/follow", views.follow, name="follow"),
    path("api/all_posts", views.get_posts, name="all_posts"),
    path("api/following_posts", views.following_posts, name="following_posts"),
    path("api/new_post", views.new_post, name="new_post"),
    path("api/edit_post", views.edit_post, name="edit_post"),
    path("api/like_post", views.like_post, name="like_post"),
    path("api/new_comment", views.new_comment, name="new_comment"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
