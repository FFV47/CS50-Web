from time import sleep

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as ModelError
from django.db.models import Case, Count, Q, When
from django.http import HttpRequest
from django.utils import timezone
from ninja import NinjaAPI
from ninja.errors import ValidationError as PydanticError
from ninja.security import django_auth

from network.utility import posts_pager

from .models import Comment, Post, User
from .schemas import (
    CommentIn,
    CommentOut,
    EditedPost,
    Error,
    PaginatedPosts,
    PostIn,
    PostOut,
    Username,
    UserOut,
)

# It's needed to add Ninja namespace inside the Django app namespace
api = NinjaAPI(csrf=True, auth=django_auth, urls_namespace="network:api")

# -------------------
# Exception Handling
# -------------------


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


# ----------
# API Views
# ----------
@api.post("/new_post", url_name="new_post", response=PostOut)
def new_post(request: HttpRequest, new_post: PostIn):
    """
    Create a new post.
    """
    post = Post.objects.create(user=request.user, text=new_post.text)
    post.liked_by.add(request.user)
    post.likes = 1
    post.liked_by_user = True

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

    # Finally, realize that update() does an update at the SQL level
    # and, thus, does not call any save() methods on your models, nor
    # does it emit the pre_save or post_save signals
    # https://docs.djangoproject.com/en/4.0/ref/models/querysets/#update
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


@api.post("/new_comment", url_name="new_comment", response=CommentOut)
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

    return Comment.objects.create(
        post=post,
        user=request.user,
        text=new_comment.text,
        reply=reply,
        parent_comment=parent_comment,
    )


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
    user_liked_posts = []
    if request.user.is_authenticated:
        user_liked_posts = [post.id for post in request.user.liked_posts.all()]  # type: ignore
    posts = (
        Post.objects.select_related("user")
        .prefetch_related("liked_by", "comments")
        .order_by("-publication_date")
        .annotate(likes=Count("liked_by"))
        .annotate(
            liked_by_user=Case(When(id__in=user_liked_posts, then=True), default=False)
        )
    )

    if len(posts) == 0:
        return 404, {"error": "No posts found."}

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
        user_liked_posts = [post.id for post in request.user.liked_posts.all()]  # type: ignore

        posts = (
            Post.objects.select_related("user")
            .prefetch_related("liked_by", "comments")
            .filter(user__username=payload.username)
            .annotate(likes=Count("liked_by"))
            .annotate(
                liked_by_user=Case(
                    When(id__in=user_liked_posts, then=True), default=False
                )
            )
        )

    if posts is None or len(posts) == 0:
        return 404, {"error": "No posts found."}

    return posts_pager(posts, page)


@api.post("/follow", url_name="follow")
def follow(request: HttpRequest, payload: Username):
    username = payload.username
    user = User.objects.get(username=username)

    if user in request.user.following.all():  # type: ignore
        request.user.following.remove(user)  # type: ignore
        return {"message": f"Unfollowed {username}."}

    request.user.following.add(user)  # type: ignore
    return {"message": f"You are now following {username}."}


@api.get("/following_posts", url_name="following_posts", response=list[PostOut])
def following_posts(request: HttpRequest):
    user_liked_posts = [post.id for post in request.user.liked_posts.all()]  # type: ignore

    posts = (
        Post.objects.filter(user__in=request.user.following.all())  # type: ignore
        .annotate(likes=Count("liked_by"))
        .annotate(
            liked_by_user=Case(When(id__in=user_liked_posts, then=True), default=False)
        )
    )
    return posts


@api.get("/profile", url_name="profile", response=UserOut)
def profile(request: HttpRequest):
    # select_related() only works with foreign key and one-to-one fields
    user = User.objects.prefetch_related(
        "following", "posts", "liked_posts", "comments", "followers"
    ).get(
        id=request.user.id  # type: ignore
    )
    return user
