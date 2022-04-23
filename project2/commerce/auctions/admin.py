from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Comment, User, Category, Listing, Bid


class ListingAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "price", "active"]
    list_display_links = ["id", "title", "price", "active"]
    filter_horizontal = ("bidders",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "post"]
    list_display_links = ["id", "author", "post"]


class BidAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "listing", "value"]
    list_display_links = ["id", "user", "listing", "value"]


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
