from django.contrib import admin

from .models import User, Post, Comment


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name")


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
