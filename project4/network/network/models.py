from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import UserManager
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import (
    Case,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    QuerySet,
    Value,
    When,
)
from django.forms import ValidationError

from .utility import FileValidator, upload_path

file_validator = FileValidator(max_size=2.5, content_types=("image/jpeg", "image/png"))

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

# region Managers


class CustomUserManager(UserManager):
    def fetch_profile(self, request_user: User, username: str):
        # select_related() only works with foreign key and one-to-one
        # fields
        is_owner = Case(When(user__id=request_user.id, then=True), default=False)
        is_following = Exists(request_user.following.filter(id=OuterRef("user__id")))
        liked_by_user = Exists(request_user.liked_posts.filter(id=OuterRef("id")))

        return self.prefetch_related(
            Prefetch(
                "posts",
                queryset=Post.objects.select_related()
                .prefetch_related(
                    Prefetch(
                        "comments",
                        queryset=Comment.objects.select_related().filter(reply=False),
                    ),  # filter related "comments" inside the post QuerySet
                )
                .order_by("-publication_date")
                .annotate(is_following=is_following)
                .annotate(is_owner=is_owner)
                .annotate(likes=Count("liked_by"))
                .annotate(liked_by_user=liked_by_user),
            )
        ).get(username=username)


class PostManager(models.Manager):
    def request_data(self, request_user):
        liked_by_user = Value(False)
        is_following = Value(False)
        is_owner = Case(When(user__id=request_user.id, then=True), default=False)

        if request_user.is_authenticated:
            # Check if the user has liked the post in each row of the query
            liked_by_user = Exists(request_user.liked_posts.filter(id=OuterRef("id")))
            is_following = Exists(request_user.following.filter(id=OuterRef("user__id")))

        return is_owner, liked_by_user, is_following

    def fetch_all_posts(self, request_user) -> QuerySet[Post]:
        is_owner, liked_by_user, is_following = self.request_data(request_user)

        return (
            self.select_related()
            .prefetch_related(
                Prefetch(
                    "comments",
                    queryset=Comment.objects.select_related().filter(reply=False),
                ),  # filter related "comments" inside the post QuerySet
            )
            .order_by("-publication_date")
            .annotate(is_following=is_following)
            .annotate(is_owner=is_owner)
            .annotate(likes=Count("liked_by"))
            .annotate(liked_by_user=liked_by_user)
        )

    def fetch_following_posts(self, request_user: User) -> QuerySet[Post]:
        return self.fetch_all_posts(request_user).filter(
            user__in=request_user.following.all()
        )


# endregion


# region Models


class User(AbstractUser):
    id: int
    posts: RelatedManager[Post]
    liked_posts: RelatedManager[Post]
    comments: RelatedManager[Comment]

    about = models.CharField(blank=True, max_length=255)
    photo = models.ImageField(
        blank=True,
        null=True,
        upload_to=upload_path,
        validators=[file_validator],
    )

    following = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False
    )

    objects: CustomUserManager = CustomUserManager()

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

    def __str__(self):
        return f"{self.username}"  # type: ignore


class Post(models.Model):
    id: int
    user_id: int
    comments: RelatedManager[Comment]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    text = models.CharField(max_length=200)
    publication_date = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )

    # Related Fields
    # comments = ManyToOne("Comment", related_name="post")

    objects: PostManager = PostManager()

    class Meta:
        ordering = ["-publication_date"]

    def __str__(self):
        return f"{self.text}"


class Comment(models.Model):
    id: int
    post_id: int
    user_id: int
    parent_comment_id: int
    replies: RelatedManager[Comment]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.CharField(max_length=200)
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


# endregion
