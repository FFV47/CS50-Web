from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_image_file_extension
from django.db import models
from django.forms import ValidationError

from .utility import file_size, upload_path


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

    # Related fields
    # posts = ManyToOne("Post", related_name="user")
    # liked_posts = ManyToMany("Post", related_name="liked_by")
    # comments = ManyToOne("Comment", related_name="user")

    def save(self, *args, **kwargs):
        """
        full_clean is not called automatically on save by Django
        """
        self.full_clean()
        super().save(*args, **kwargs)

    # def profile_posts(self):
    #     return [
    #         {
    #             "text": post.text,
    #             "publication_date": post.publication_date.strftime("%H:%M %d/%m/%Y"),
    #             "likes": post.likes,
    #         }
    #         for post in self.posts.all()  # type: ignore
    #     ]

    def __str__(self):
        return f"{self.username}"  # type: ignore


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    text = models.TextField()
    publication_date = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )

    # Related Fields
    # comments = ManyToOne("Comment", related_name="post")

    class Meta:
        ordering = ["-publication_date"]

    def __str__(self):
        return f"{self.text}"


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

    def __str__(self):
        return f"{self.text} - reply: {self.reply}"  # type: ignore
