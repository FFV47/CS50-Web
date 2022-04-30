from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError as ModelError
from django.db.models import Q
from ninja import NinjaAPI
from ninja.errors import ValidationError as PydanticError
from ninja.security import django_auth

from .models import Comment, Post, User
from .schemas import CommentIn, Error, PostIn, PostOut, Username, UserOut

# It's needed to add Ninja namespace inside the Django app namespace
api = NinjaAPI(csrf=True, auth=django_auth, urls_namespace="network:rest_api")

# ----------
# Exception Handling
# ----------


@api.exception_handler(ObjectDoesNotExist)
def object_not_found(request, exc):
    return api.create_response(
        request, {"errors": "The requested object does not exist."}, status=404
    )


@api.exception_handler(ModelError)
def django_model_validation(request, exc):
    return api.create_response(request, exc.message_dict, status=400)


@api.exception_handler(PydanticError)
def pydantic_validation(request, exc):
    for obj in exc.errors:
        obj["field"] = obj["loc"][-1]
        del obj["loc"]
    errors = {"errors": exc.errors}
    return api.create_response(request, errors, status=400)


# ----------
# API Views
# ----------
@api.post("/new_post", url_name="new_post")
def new_post(request, new_post: PostIn):

    Post.objects.create(user=request.user, text=new_post.text)

    return {"message": "Post created successfully."}


@api.post("/edit_post", url_name="edit_post")
def edit_post(request, edited_post: PostIn):
    # Query lookup with Q objects
    # https://docs.djangoproject.com/en/4.0/topics/db/queries/#complex-lookups-with-q
    # When an operator (| or &) is used on two Q objects, it yields a new Q
    # object (which is a unique constraint), which is ideal for get lookup.
    post = Post.objects.get(Q(user=request.user) & Q(id=edited_post.post_id))
    post.text = edited_post.text
    post.save()

    return {"message": "Post edited successfully."}


@api.patch("/like_post/{int:post_id}", url_name="like_post")
def like_post(request, post_id: int):
    post = Post.objects.get(id=post_id)
    if post in request.user.liked_posts.all():
        request.user.liked_posts.remove(post)
        return {"message": "Post unliked"}

    request.user.liked_posts.add(post)
    return {"message": "Post liked"}


@api.post("/new_comment", url_name="new_comment")
def new_comment(request, new_comment: CommentIn):
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

    return {"message": "Comment created successfully."}


@api.api_operation(
    ["GET", "POST"],
    "/all_posts",
    url_name="all_posts",
    auth=None,
    response={400: Error, 200: list[PostOut]},
)
def get_all_posts(request, payload: Username = Username()):
    """
    When defined, the payload cannot be empty. To be able to send an
    empty payload, the default value was defined as a empty Schema
    (Pydantic Model)
    """
    if request.method == "POST":
        if request.user.is_authenticated is False:
            return 400, {
                "error": "You must be logged in to query posts from selected user."
            }
        if request.user.is_authenticated and payload.username:
            posts = (
                Post.objects.select_related("user")
                .prefetch_related("liked_by", "comments")
                .filter(user__username=payload.username)
            )
            return posts

    posts = (
        Post.objects.select_related("user").prefetch_related("liked_by", "comments").all()
    )
    return posts


@api.post("/follow", url_name="follow")
def follow(request, payload: Username):
    username = payload.username
    user = User.objects.get(username=username)

    if user in request.user.following.all():
        request.user.following.remove(user)
        return {"message": f"Unfollowed {username}."}

    request.user.following.add(user)
    return {"message": f"You are now following {username}."}


@api.get("/following_posts", url_name="following_posts", response=list[PostOut])
def following_posts(request):
    posts = Post.objects.filter(user__in=request.user.following.all())
    return posts


@api.get("/profile", url_name="profile", response=UserOut)
def profile(request):
    # select_related() only works with foreign key and one-to-one fields
    user = User.objects.prefetch_related(
        "following", "posts", "liked_posts", "comments", "followers"
    ).get(id=request.user.id)
    return user
