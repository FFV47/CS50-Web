from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from auctions import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watch/<int:listing_id>", views.watch, name="watch"),
    path("user_listings/<int:user_id>", views.user_listings, name="user_listings"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category_listing, name="category_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("listing/<int:listing_id>", views.detail_listing, name="detail_listing"),
    path(
        "listing/<int:listing_id>/comment",
        views.comment_listing,
        name="comment_listing",
    ),
    path("listing/<int:listing_id>/bid", views.bid_listing, name="bid_listing"),
    path("listing/<int:listing_id>/edit", views.edit_listing, name="edit_listing"),
    path("listing/<int:listing_id>/close", views.close_listing, name="close_listing"),
    path("listing/<int:listing_id>/delete", views.delete_listing, name="delete_listing"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize 404 error page
# handler404 = 'mysite.views.my_custom_page_not_found_view'

# handler404
# A callable, or a string representing the full Python import path to the view that should be called if none of the URL patterns match.

# By default, this is django.views.defaults.page_not_found(). If you implement a custom view, be sure it accepts request and exception arguments and returns an HttpResponseNotFound.
