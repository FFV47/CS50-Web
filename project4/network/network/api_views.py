from time import sleep
from typing import Any
from unicodedata import normalize

import orjson
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as ModelError
from django.core.files.storage import default_storage
from django.core.paginator import InvalidPage, Paginator
from django.db.models import Prefetch, Q, QuerySet, prefetch_related_objects
from django.forms import modelform_factory
from django.http import HttpRequest
from django.utils import timezone
from ninja import Form, NinjaAPI
from ninja.errors import ValidationError as PydanticError
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from ninja.responses import Response
from ninja.security import django_auth

from .models import Comment, Post, User
from .schemas import (
    CommentIn,
    EditedPost,
    FollowOut,
    PaginatedPosts,
    PostIn,
    PostOut,
    UserOut,
    UserProfileIn,
    UserProfileOut,
)


class ORJSONParser(Parser):
    def parse_body(self, request):
        return orjson.loads(request.body)


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data, option=orjson.OPT_UTC_Z | orjson.OPT_OMIT_MICROSECONDS)


class AuthHttpRequest(HttpRequest):
    user: User


# It's needed to add Ninja namespace inside the Django app namespace
api = NinjaAPI(
    parser=ORJSONParser(),
    renderer=ORJSONRenderer(),
    csrf=True,
    auth=django_auth,
    urls_namespace="network:api",
)

# --------------------
# region Exception Handling
# --------------------


@api.exception_handler(ObjectDoesNotExist)
def object_not_found(request: HttpRequest, exc):
    return api.create_response(
        request, {"errors": "The requested object does not exist."}, status=404
    )


@api.exception_handler(ModelError)
def django_model_validation(request: HttpRequest, exc):
    return api.create_response(request, exc.message_dict, status=400)


@api.exception_handler(PydanticError)
def pydantic_validation(request: HttpRequest, exc):
    for obj in exc.errors:
        obj["field"] = obj["loc"][-1]
        del obj["loc"]
    errors = {"errors": exc.errors}
    return api.create_response(request, errors, status=400)


# endregion

# -----------
# region API Views
# -----------
@api.post("new_post", url_name="new_post", response=PostOut)
def new_post(request: AuthHttpRequest, new_post: PostIn):
    """
    Create a new post.
    """
    post = Post.objects.create(user=request.user, text=new_post.text)
    post.liked_by.add(request.user)
    post.is_owner = True
    post.is_following = False
    post.likes = 1
    post.liked_by_user = True

    sleep(1)

    return post


@api.post("edit_post", url_name="edit_post", response={404: Any, 200: EditedPost})
def edit_post(request: AuthHttpRequest, edited_post: PostIn):
    """
    Edit a post.
    """
    # Query lookup with Q objects
    # https://docs.djangoproject.com/en/4.0/topics/db/queries/#complex-lookups-with-q
    # When an operator (| or &) is used on two Q objects, it yields a new Q
    # object (which is a unique constraint), which is ideal for get
    # lookup.

    try:
        post = Post.objects.get(Q(user=request.user) & Q(id=edited_post.post_id))
    except Post.DoesNotExist:
        return 404, {"error": "Post not found."}

    post.text = edited_post.text
    post.last_modified = timezone.now()
    post.edited = True
    post.save()

    sleep(1)  # Simulate a slow network connection
    return post


@api.patch("like_post/{int:post_id}", url_name="like_post")
def like_post(request: AuthHttpRequest, post_id: int):
    """
    Like a post by ID.
    """
    post: Post = Post.objects.get(id=post_id)
    if post in request.user.liked_posts.all():
        request.user.liked_posts.remove(post)
        return {"id": post.id, "likes": post.liked_by.count(), "likedByUser": False}

    request.user.liked_posts.add(post)
    return {"id": post.id, "likes": post.liked_by.count(), "likedByUser": True}


@api.post("new_comment", url_name="new_comment", response=PostOut)
def new_comment(request: AuthHttpRequest, new_comment: CommentIn):
    """
    Create a new comment on a post.
    """
    post = Post.objects.get(id=new_comment.post_id)

    try:
        parent_comment = Comment.objects.get(id=new_comment.parent_comment_id)
        reply = True
    except Comment.DoesNotExist:
        parent_comment = None
        reply = False

    Comment.objects.create(
        post=post,
        user=request.user,
        text=new_comment.text,
        reply=reply,
        parent_comment=parent_comment,
    )
    post.refresh_from_db()
    prefetch_related_objects(
        [post],
        Prefetch(
            "comments", queryset=Comment.objects.select_related().filter(reply=False)
        ),
    )
    post.is_owner = post.user.id == request.user.id
    post.is_following = request.user in post.user.followers.all()
    post.likes = post.liked_by.count()
    post.liked_by_user = request.user in post.liked_by.all()

    sleep(1)
    return post


@api.get(
    "all_posts/{int:page}",
    url_name="all_posts",
    auth=None,
    response=PaginatedPosts,
)
def get_all_posts(request: HttpRequest, page: int):
    """
    Fetch all posts from the database. These posts can be shown to unauthenticated users.
    """

    posts = Post.objects.fetch_all_posts(request_user=request.user)

    if posts is None or posts.exists() is False:
        return Response({"posts": []})

    # sleep(3)

    return posts_pager(posts, page)


@api.post("follow/{str:username}", url_name="follow", response=FollowOut)
def follow(request: AuthHttpRequest, username: str):
    user = User.objects.get(username=username)

    if user in request.user.following.all():
        request.user.following.remove(user)
        return {
            "message": f"You are no longer following {username}",
            "is_following": False,
        }

    request.user.following.add(user)
    return {"message": f"You are now following {username}", "is_following": True}


@api.get(
    "following_posts/{int:page}", url_name="following_posts", response=PaginatedPosts
)
def following_posts(request: AuthHttpRequest, page: int):

    posts = Post.objects.fetch_following_posts(request.user)

    return posts_pager(posts, page)


@api.get("profile/{str:username}/{int:page}", url_name="profile", response=UserOut)
def profile(request: AuthHttpRequest, username: str, page: int):

    profile_user = User.objects.fetch_profile(request.user, username)

    profile_user.is_following = request.user in profile_user.followers.all()
    profile_user.posts_data = posts_pager(profile_user.posts.all(), page)

    # sleep(3)

    return profile_user


@api.post("update_profile", url_name="update_profile", response=UserProfileOut)
def update_profile(request: AuthHttpRequest, profile: UserProfileIn = Form(...)):
    errors = {}

    # Validate changes to username and email
    if (
        request.user.username != profile.username
        and User.objects.filter(username=profile.username).exists()
    ):
        errors["username"] = f"Username {profile.username} is already in use."

    if (
        request.user.email != profile.email
        and User.objects.filter(email=profile.email).exists()
    ):
        errors["email"] = f"{profile.email} is already in use."

    previous_image_path = None
    if request.user.photo:
        previous_image_path = request.user.photo.path
    # Create a form to validate uploaded file
    ProfileForm = modelform_factory(User, fields=("username", "email", "photo", "about"))
    form = ProfileForm(profile.dict(), request.FILES, instance=request.user)

    if not errors and form.is_valid():
        if form.cleaned_data["photo"] and previous_image_path:
            default_storage.delete(previous_image_path)
        user = form.save()
        return user
    else:
        if form.errors.get("photo"):
            image_error = normalize(
                "NFKD", form.errors.get_json_data()["photo"][0]["message"]
            )
            errors["photo"] = image_error

        # Response bypass default response schema, allowing any JSON structure
        return Response({"errors": errors})


# endregion

# -----------
# region Functions
# -----------
def posts_pager(posts: QuerySet[Post], page: int):
    p = Paginator(posts, 10)

    p_page = p.get_page(page)

    try:
        next_page = p_page.next_page_number()
    except InvalidPage:
        next_page = None

    try:
        previous_page = p_page.previous_page_number()
    except InvalidPage:
        previous_page = None

    # Cast "QuerySet" to "list" to be parsed by Pydantic Model
    return {
        "numPages": p.num_pages,
        "nextPage": next_page,
        "previousPage": previous_page,
        "posts": list(p_page.object_list),
    }


# endregion
