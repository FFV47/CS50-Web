from time import sleep

import orjson
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as ModelError
from django.core.paginator import InvalidPage, Paginator
from django.db.models import (
    Case,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Q,
    Value,
    When,
    prefetch_related_objects,
)
from django.http import HttpRequest
from django.utils import timezone
from ninja import NinjaAPI
from ninja.errors import ValidationError as PydanticError
from ninja.renderers import BaseRenderer
from ninja.security import django_auth

from .models import Comment, Post, User
from .schemas import (
    CommentIn,
    EditedPost,
    Error,
    FollowOut,
    PaginatedPosts,
    PostIn,
    PostOut,
    Username,
    UserOut,
)


class ORJSONRenderer(BaseRenderer):
    media_type = "application/json"

    def render(self, request, data, *, response_status):
        return orjson.dumps(data, option=orjson.OPT_UTC_Z | orjson.OPT_OMIT_MICROSECONDS)


# It's needed to add Ninja namespace inside the Django app namespace
api = NinjaAPI(
    renderer=ORJSONRenderer(), csrf=True, auth=django_auth, urls_namespace="network:api"
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
@api.post("/new_post", url_name="new_post", response=PostOut)
def new_post(request: HttpRequest, new_post: PostIn):
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


@api.post("/edit_post", url_name="edit_post", response=EditedPost)
def edit_post(request: HttpRequest, edited_post: PostIn):
    """
    Edit a post.
    """
    # Query lookup with Q objects
    # https://docs.djangoproject.com/en/4.0/topics/db/queries/#complex-lookups-with-q
    # When an operator (| or &) is used on two Q objects, it yields a new Q
    # object (which is a unique constraint), which is ideal for get
    # lookup.

    post = Post.objects.get(Q(user=request.user) & Q(id=edited_post.post_id))
    post.text = edited_post.text
    post.last_modified = timezone.now()
    post.edited = True
    post.save()

    sleep(1)  # Simulate a slow network connection
    return post


@api.patch("/like_post/{int:post_id}", url_name="like_post")
def like_post(request: HttpRequest, post_id: int):
    """
    Like a post by ID.
    """
    post = Post.objects.get(id=post_id)
    if post in request.user.liked_posts.all():  # type: ignore
        request.user.liked_posts.remove(post)  # type: ignore
        return {"id": post.id, "likes": post.liked_by.count(), "likedByUser": False}

    request.user.liked_posts.add(post)  # type: ignore
    return {"id": post.id, "likes": post.liked_by.count(), "likedByUser": True}


@api.post("/new_comment", url_name="new_comment", response=PostOut)
def new_comment(request: HttpRequest, new_comment: CommentIn):
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
    post.is_owner = post.user.id == request.user.id  # type: ignore
    post.is_following = request.user in post.user.followers.all()
    post.likes = post.liked_by.count()
    post.liked_by_user = request.user in post.liked_by.all()

    sleep(1)
    return post


@api.get(
    "/all_posts/{int:page}",
    url_name="all_posts",
    auth=None,
    response={404: Error, 200: PaginatedPosts},
)
def get_all_posts(request: HttpRequest, page: int):
    """
    Fetch all posts from the database. These posts can be shown to unauthenticated users.
    """

    posts = get_posts_queryset(request.user)

    if posts is None or posts.exists() is False:
        return 404, {"error": "No posts found."}

    # sleep(20)

    return posts_pager(posts, page)


@api.post(
    "/user_posts/{int:page}",
    url_name="user_posts",
    response={401: Error, 404: Error, 200: PaginatedPosts},
)
def get_user_posts(request: HttpRequest, page: int, payload: Username = Username()):
    """
    Fetch posts from a specific user.

    Observation:
    To declare a request body, you need to use Django Ninja
    Schema (Pydantic Model). When defined, the payload cannot be empty. To be able to
    send an empty payload, the default value must be defined as a Schema
    with all fields optional
    """
    posts = None
    if payload.username:
        is_owner = Case(When(user__id=request.user.id, then=True), default=False)  # type: ignore

        liked_by_user = Exists(request.user.liked_posts.filter(id=OuterRef("id")))  # type: ignore
        is_following = Exists(request.user.following.filter(id=OuterRef("user__id")))  # type: ignore

        posts = (
            Post.objects.select_related()
            .prefetch_related(
                Prefetch(
                    "comments",
                    queryset=Comment.objects.select_related().filter(reply=False),
                ),  # filter related "comments" inside the post QuerySet
            )
            .filter(user__username=payload.username)
            .order_by("-publication_date")
            .annotate(is_following=is_following)
            .annotate(is_owner=is_owner)
            .annotate(likes=Count("liked_by"))
            .annotate(liked_by_user=liked_by_user)
        )

    if posts is None or posts.exists() is False:
        return 404, {"error": "No posts found."}

    return posts_pager(posts, page)


@api.post("/follow", url_name="follow", response=FollowOut)
def follow(request: HttpRequest, payload: Username):
    username = payload.username
    user = User.objects.get(username=username)

    if user in request.user.following.all():  # type: ignore
        request.user.following.remove(user)  # type: ignore
        return {
            "message": f"You are no longer following {username}",
            "is_following": False,
        }

    request.user.following.add(user)  # type: ignore
    return {"message": f"You are now following {username}", "is_following": True}


@api.get("/following_posts", url_name="following_posts", response=list[PostOut])
def following_posts(request: HttpRequest):

    return get_posts_queryset(request.user)


@api.get("/profile/{str:username}", url_name="profile", response=UserOut)
def profile(request: HttpRequest, username: str):
    # select_related() only works with foreign key and one-to-one
    # fields

    is_following = Exists(request.user.following.filter(id=OuterRef("user__id")))  # type: ignore
    is_owner = Case(When(user__id=request.user.id, then=True), default=False)  # type: ignore
    liked_by_user = Exists(request.user.liked_posts.filter(id=OuterRef("id")))  # type: ignore

    profile_user = User.objects.prefetch_related(
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

    return profile_user


# endregion

# -----------
# region Functions
# -----------
def posts_pager(posts, page):
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


def get_posts_queryset(user):
    liked_by_user = Value(False)
    is_following = Value(False)
    is_owner = Case(When(user__id=user.id, then=True), default=False)
    if user.is_authenticated:
        # Check if the user has liked the post in each row of the query
        liked_by_user = Exists(user.liked_posts.filter(id=OuterRef("id")))  # type: ignore
        is_following = Exists(user.following.filter(id=OuterRef("user__id")))  # type: ignore

    posts = (
        Post.objects.select_related()
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

    return posts


# endregion
