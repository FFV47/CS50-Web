from django.contrib import admin

from .models import User, Post, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name")


class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "text", "publication_date", "edited")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "text", "publication_date")


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
