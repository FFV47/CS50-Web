from __future__ import annotations
from datetime import datetime

from re import search

# from django.utils import timezone
from ninja import Field, ModelSchema, Schema
from pydantic import constr, validator

from .models import Comment, Post, User


# def format_date(datetime: timezone.datetime):
#     return timezone.localtime(datetime).strftime("%B %d, %Y - %H:%M")


def must_not_be_html(string):
    if search("<(\"[^\"]*\"|'[^']*'|[^'\">])*>", string):
        raise ValueError("HTML is not allowed.")
    return string


# ----------
# region User
# ----------


class UserOut(ModelSchema):
    # "..." means the field is required
    lastLogin: datetime = Field(..., alias="last_login")
    dateJoined: datetime = Field(..., alias="date_joined")
    followingCount: int = Field(..., alias="following.count")
    followersCount: int = Field(..., alias="followers.count")
    isFollowing: bool = Field(..., alias="is_following")
    postsData: PaginatedPosts = Field(..., alias="posts_data")

    class Config:
        model = User
        model_fields = [
            "username",
            "about",
            "photo",
            "email",
        ]


class UserProfileIn(Schema):
    username: constr(strip_whitespace=True, min_length=3, max_length=20)  # type: ignore
    about: constr(strip_whitespace=True, max_length=200)  # type: ignore
    email: constr(strip_whitespace=True)  # type: ignore


class UserProfileOut(ModelSchema):
    class Config:
        model = User
        model_fields = ["username", "email", "photo", "about"]


class FollowOut(Schema):
    message: str
    isFollowing: bool = Field(..., alias="is_following")


# endregion

# ----------
# region Post
# ----------


class PostIn(Schema):
    post_id: int | None = Field(None, alias="postID")
    text: constr(strip_whitespace=True)  # type: ignore

    block_html = validator("text", allow_reuse=True)(must_not_be_html)

    @validator("text")
    def text_size(cls, value):
        if len(value) < 3:
            raise ValueError("Post must be at least 3 characters long.")
        if len(value) > 200:
            raise ValueError("Post must be at most 200 characters long.")
        return value


class PostOut(ModelSchema):
    username: str = Field(..., alias="user.username")
    isFollowing: bool = Field(..., alias="is_following")
    isOwner: bool = Field(..., alias="is_owner")
    likes: int = Field(..., alias="likes")
    likedByUser: bool = Field(False, alias="liked_by_user")
    publicationDate: datetime = Field(..., alias="publication_date")
    lastModified: datetime = Field(..., alias="last_modified")
    comments: list[CommentOut] = Field(..., alias="comments")

    class Config:
        model = Post
        model_fields = ["id", "text", "edited"]


class EditedPost(ModelSchema):
    lastModified: datetime = Field(..., alias="last_modified")

    class Config:
        model = Post
        model_fields = ["id", "text", "edited"]


class PaginatedPosts(Schema):
    numPages: int
    previousPage: int | None = None
    nextPage: int | None = None
    posts: list[PostOut]


# endregion
# ----------
# region Comment
# ----------


class CommentIn(Schema):
    text: constr(strip_whitespace=True, max_length=200, min_length=3)  # type: ignore
    post_id: int = Field(..., alias="postID")
    parent_comment_id: int | None = Field(None, alias="commentID")

    block_html = validator("text", allow_reuse=True)(must_not_be_html)


class CommentOut(ModelSchema):
    username: str = Field(..., alias="user.username")
    publicationDate: datetime = Field(..., alias="publication_date")
    replies: list[CommentOut] = Field(..., alias="replies")

    class Config:
        model = Comment
        model_fields = ["id", "text"]


# endregion

# Self-referencing schemes
UserOut.update_forward_refs()
PostOut.update_forward_refs()
CommentOut.update_forward_refs()
