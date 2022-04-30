from __future__ import annotations

from re import search

from django.utils import timezone
from ninja import Field, ModelSchema, Schema
from pydantic import constr, validator

from .models import Comment, Post, User


class Username(Schema):
    username: str | None = None


class Error(Schema):
    error: str


def format_date(datetime: timezone.datetime):
    return timezone.localtime(datetime).strftime("%H:%M %d/%m/%Y")


def must_not_be_html(string):
    if search("<(\"[^\"]*\"|'[^']*'|[^'\">])*>", string):
        raise ValueError("HTML is not allowed.")
    return string


class UserOut(ModelSchema):
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

    def resolve_date_joined(self, obj):
        return format_date(obj.date_joined)

    def resolve_last_login(self, obj):
        return format_date(obj.last_login)


class PostIn(Schema):
    post_id: int | None
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
    likedBy: list[Username] = Field(..., alias="liked_by")
    publicationDate: str = Field(..., alias="publication_date")
    lastModified: str = Field(..., alias="last_modified")
    comments: list[CommentOut] = Field(..., alias="comments")

    class Config:
        model = Post
        model_fields = ["id", "text"]

    def resolve_publication_date(self, obj):
        return format_date(obj.publication_date)

    def resolve_last_modified(self, obj):
        return format_date(obj.last_modified)

    def resolve_comments(self, obj):
        return obj.comments.filter(reply=False)


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

    def resolve_publication_date(self, obj):
        return format_date(obj.publication_date)


UserOut.update_forward_refs()
PostOut.update_forward_refs()
CommentOut.update_forward_refs()
