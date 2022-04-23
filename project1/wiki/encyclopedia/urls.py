from django.urls import path

from encyclopedia import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.entry_page, name="entry_page"),
    path("search_entry", views.search_entry, name="search_entry"),
    path("new_entry", views.new_entry, name="new_entry"),
    path("edit_entry/<entry>", views.edit_entry, name="edit_entry"),
    path("rand_entry", views.rand_entry, name="rand_entry"),
    path("error", views.error, name="error"),
]
