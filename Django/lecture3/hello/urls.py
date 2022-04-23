from django.urls.conf import path
from hello import views

urlpatterns = [
    path("", views.index, name="index"),
    path("fernando", views.fernando, name="fernando"),
    path("<str:name>", views.greeting, name="greeting"),
]
