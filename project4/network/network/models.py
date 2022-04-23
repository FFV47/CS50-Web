from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    validate_image_file_extension,
    MinLengthValidator,
    MaxLengthValidator,
)
from django.db import models
from django.forms import ValidationError

from .utility import file_size, upload_path

min_length_valid = MinLengthValidator(5, "Post must be at least 5 characters long.")
max_lenght_valid = MaxLengthValidator(280, "Post must be at most 280 characters long.")


class User(AbstractUser):
    photo = models.ImageField(
        blank=True,
        null=True,
        upload_to=upload_path,
        validators=[file_size, validate_image_file_extension],
    )

    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False
    )

    def save(self, *args, **kwargs):
        """
        full_clean is not called automatically on save by Django
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def to_json(self):
        return {
            "id": self.id,  # type: ignore
            "username": self.get_username(),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.get_full_name(),
            "email": self.email,
            "following": [user.to_json() for user in self.following.all()],
            "followers": [user.to_json() for user in self.followers.all()],  # type: ignore
            "posts": [post.to_json() for post in self.posts.all()],  # type: ignore
            "date_joined": self.date_joined.strftime("%H:%M %d/%m/%Y"),
        }

    def profile_posts(self):
        return [
            {
                "text": post.text,
                "publication_date": post.publication_date.strftime("%H:%M %d/%m/%Y"),
                "likes": post.likes,
            }
            for post in self.posts.all()  # type: ignore
        ]

    def __str__(self):
        return f"{self.username}"  # type: ignore


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    text = models.TextField(validators=[min_length_valid, max_lenght_valid])
    publication_date = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts"
    )

    class Meta:
        ordering = ["-publication_date"]

    def save(self, *args, **kwargs):
        """
        Exclude "likes" from full_clean, because F() expressions
        are only evaluated after save().
        """
        self.full_clean(exclude=["likes"])
        super().save(*args, **kwargs)

    def to_json(self):
        return {
            "id": self.id,  # type: ignore
            "user": self.user.username,
            "text": self.text,
            "publication_date": self.publication_date.strftime("%H:%M %d/%m/%Y"),
            "liked_by": [user.username for user in self.liked_by.all()],
            "comments": [comment.to_json() for comment in self.comments.all()],  # type: ignore
        }

    def get_comments(self):
        return [comment.to_json() for comment in self.comments.all()]  # type: ignore

    def __str__(self):
        return f"{self.text} - {self.likes}"  # type: ignore


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.CharField(max_length=255)
    publication_date = models.DateTimeField(auto_now_add=True)
    reply = models.BooleanField(default=False)
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    class Meta:
        ordering = ["-publication_date"]

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.parent_comment is not None:
            if self.parent_comment.post.id != self.post.id:
                raise ValidationError("Parent comment must be from the same post.")
            self.reply = True
        super().save(*args, **kwargs)

    def to_json(self):
        if self.reply is False:
            return {
                "id": self.id,  # type: ignore
                "user": self.user.username,
                "text": self.text,
                "publication_date": self.publication_date.strftime("%H:%M %d/%m/%Y"),
                "replies": [reply.reply_json() for reply in self.replies.all()] if self.replies.exists() else None,  # type: ignore
            }
        else:
            return None

    def reply_json(self):
        return {
            "user": self.user.username,
            "text": self.text,
            "publication_date": self.publication_date.strftime("%H:%M %d/%m/%Y"),
            "replies": [reply.to_json() for reply in self.replies.all()] if self.replies.exists() else None,  # type: ignore
            "parent_id": self.parent_comment.id if self.parent_comment is not None else None,  # type: ignore
        }

    def __str__(self):
        return f"{self.text} - reply: {self.reply}"  # type: ignore
