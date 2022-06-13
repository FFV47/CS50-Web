from __future__ import annotations

from re import search

from django.utils import timezone
from ninja import Field, ModelSchema, Schema
from pydantic import constr, validator

from .models import Comment, Post, User


def format_date(datetime: timezone.datetime):
    return timezone.localtime(datetime).strftime("%B %d, %Y - %H:%M")


def must_not_be_html(string):
    if search("<(\"[^\"]*\"|'[^']*'|[^'\">])*>", string):
        raise ValueError("HTML is not allowed.")
    return string


class Error(Schema):
    error: str


# ----------
# * User
# ----------


class Username(Schema):
    username: str | None = None


class UserOut(ModelSchema):
    # "..." means the field is required
    firstName: str = Field(..., alias="first_name")
    lastName: str = Field(..., alias="last_name")
    lastLogin: str = Field(..., alias="last_login")
    dateJoined: str = Field(..., alias="date_joined")
    posts: list[PostOut] = Field(..., alias="posts")
    comments: list[CommentOut] = Field(..., alias="comments")
    following: list[Username]
    followers: list[Username] = Field(..., alias="followers")

    class Config:
        model = User
        model_fields = [
            "id",
            "username",
            "photo",
            "email",
        ]

    @staticmethod
    def resolve_date_joined(obj):
        return format_date(obj.date_joined)

    @staticmethod
    def resolve_last_login(obj):
        return format_date(obj.last_login)


# ----------
# * Post
# ----------


class PostIn(Schema):
    post_id: int | None = Field(None, alias="postID")
    text: constr(strip_whitespace=True)  # type: ignore

    block_html = validator("text", allow_reuse=True)(must_not_be_html)

    @validator("text")
    def text_size(cls, value):
        if len(value) < 5:
            raise ValueError("Post must be at least 5 characters long.")
        if len(value) > 280:
            raise ValueError("Post must be at most 280 characters long.")
        return value


class PostOut(ModelSchema):
    username: str = Field(..., alias="user.username")
    likes: int = Field(..., alias="likes")
    likedByUser: bool = Field(False, alias="liked_by_user")
    publicationDate: str = Field(..., alias="publication_date")
    lastModified: str = Field(..., alias="last_modified")
    comments: list[CommentOut] = Field(..., alias="comments")

    class Config:
        model = Post
        model_fields = ["id", "text", "edited"]

    # obj parameter is the Post object from Django ORM
    @staticmethod
    def resolve_publication_date(obj):
        return format_date(obj.publication_date)

    @staticmethod
    def resolve_last_modified(obj):
        return format_date(obj.last_modified)

    @staticmethod
    def resolve_comments(obj):
        return obj.comments.filter(reply=False)

    @staticmethod
    def resolve_liked_by(obj):
        return [u.username for u in obj.liked_by.all()]


class EditedPost(ModelSchema):
    lastModified: str = Field(..., alias="last_modified")

    class Config:
        model = Post
        model_fields = ["id", "text", "edited"]

    @staticmethod
    def resolve_last_modified(obj):
        return format_date(obj.last_modified)


class PaginatedPosts(Schema):
    numPages: int
    previousPage: int | None = None
    nextPage: int | None = None
    posts: list[PostOut]


# ----------
# * Comment
# ----------


class CommentIn(Schema):
    text: constr(strip_whitespace=True)  # type: ignore
    post_id: int
    parent_comment_id: int | None

    block_html = validator("text", allow_reuse=True)(must_not_be_html)


class CommentOut(ModelSchema):
    username: str = Field(..., alias="user.username")
    publicationDate: str = Field(..., alias="publication_date")
    replies: list[CommentOut] = Field(..., alias="replies")

    class Config:
        model = Comment
        model_fields = ["id", "text"]

    @staticmethod
    def resolve_publication_date(obj):
        return format_date(obj.publication_date)


# Self-referencing schemes
UserOut.update_forward_refs()
PostOut.update_forward_refs()
CommentOut.update_forward_refs()
