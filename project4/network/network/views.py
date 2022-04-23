import json
from pydantic import ValidationError as PydanticValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.forms import ValidationError
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render

from .models import Post, User, Comment
from .json_validators import (
    EditPost,
    GetUsername,
    LikePost,
    NewComment,
    NewPost,
)


def index(request: HttpRequest):
    return render(request, "network/index.html")


def login_view(request: HttpRequest):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("network:index")
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("network:index")


def register(request: HttpRequest):
    if request.method == "POST":
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            username = request.POST["username"]
            email = request.POST["email"]
            user = User.objects.create_user(username=username, email=email, password=password)  # type: ignore
        except ValidationError as e:
            messages = " ".join(
                [f"{key}: {', '.join(value)}" for key, value in e.message_dict.items()]
            )
            return render(request, "network/register.html", {"message": messages})

        login(request, user)
        return redirect("network:index")
    else:
        return render(request, "network/register.html")


# * API views
@login_required
def new_post(request: HttpRequest):
    if request.method == "POST" and request.body:
        try:
            data_cleaned = NewPost.parse_raw(request.body).dict()
        except PydanticValidationError as e:
            message = ", ".join(
                [f"{error['loc']}: {error['msg']}" for error in json.loads(e.json())]
            )
            return JsonResponse({"error": message}, status=400)

        try:
            post = Post.objects.create(user=request.user, text=data_cleaned["post_text"])
        except ValidationError as e:
            message = "".join(
                [f"{', '.join(value)}" for value in e.message_dict.values()]
            )
            return JsonResponse({"error": message}, status=400)

        request.user.posts.add(post)  # type: ignore

        resp = {"message": "Post created successfully.", "post": post.to_json()}
        return JsonResponse(resp, status=200)
    else:
        return JsonResponse({"error": "POST request required"}, status=400)


@login_required
def edit_post(request: HttpRequest):
    if request.method == "POST" and request.body:
        try:
            data_cleaned = EditPost.parse_raw(request.body).dict()
        except PydanticValidationError as e:
            message = ", ".join(
                [f"{error['loc']}: {error['msg']}" for error in json.loads(e.json())]
            )
            return JsonResponse({"error": message}, status=400)

        post_id = data_cleaned["post_id"]
        text = data_cleaned["text"]

        post = Post.objects.get(pk=post_id)
        post.text = text
        post.save()
        return JsonResponse(
            {"message": "Post updated successfully.", "post": post.to_json()}, status=200
        )
    else:
        return JsonResponse({"error": "POST request required"}, status=400)


@login_required
def like_post(request: HttpRequest):
    if request.method == "POST" and request.body:
        try:
            data_cleaned = LikePost.parse_raw(request.body).dict()
        except PydanticValidationError as e:
            message = ", ".join(
                [f"{error['loc']}: {error['msg']}" for error in json.loads(e.json())]
            )
            return JsonResponse({"error": message}, status=400)

        post = Post.objects.get(pk=data_cleaned["post_id"])

        if request.user in post.liked_by.all():
            post.liked_by.remove(request.user)
            return JsonResponse(
                {"message": "Post unliked", "post": post.to_json()},
                status=200,
            )
        else:
            post.liked_by.add(request.user)
            return JsonResponse(
                {"message": "Post liked", "post": post.to_json()}, status=200
            )
    else:
        return JsonResponse({"error": "POST request required"}, status=400)


@login_required
def new_comment(request: HttpRequest):
    if request.method == "POST" and request.body:
        try:
            data_cleaned = NewComment.parse_raw(request.body).dict()
        except PydanticValidationError as e:
            message = ", ".join(
                [f"{error['loc']}: {error['msg']}" for error in json.loads(e.json())]
            )
            return JsonResponse({"error": message}, status=400)

        text = data_cleaned["comment_text"]
        post_id = data_cleaned["post_id"]
        parent_comment_id = data_cleaned["parent_comment_id"]

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            post = None

        try:
            parent_comment = Comment.objects.get(pk=parent_comment_id)
            reply = True
        except Comment.DoesNotExist:
            parent_comment = None
            reply = False

        try:
            comment = Comment.objects.create(
                user=request.user,
                text=text,
                post=post,
                parent_comment=parent_comment,
                reply=reply,
            )
        except ValidationError as e:
            message = "".join(
                [f"{key}: {', '.join(value)}" for key, value in e.message_dict.items()]
            )
            return JsonResponse({"error": message}, status=400)

        resp = {"message": "Comment created successfully.", "comment": comment.to_json()}
        return JsonResponse(resp, status=200)

    else:
        return JsonResponse({"error": "POST request required"}, status=400)


def get_posts(request: HttpRequest):
    if request.user.is_authenticated and request.method == "POST" and request.body:
        try:
            data_cleaned = GetUsername.parse_raw(request.body).dict()
        except PydanticValidationError as e:
            message = ", ".join(
                [f"{error['loc']}: {error['msg']}" for error in json.loads(e.json())]
            )
            return JsonResponse({"error": message}, status=400)

        username = data_cleaned["username"]

        if username:
            posts = Post.objects.filter(user__username=username)
        else:
            posts = Post.objects.all()

    elif request.method == "GET":
        posts = Post.objects.all()
    else:
        return JsonResponse(
            {"error": "GET or POST with authentication request required"}, status=400
        )

    posts = [post.to_json() for post in posts]
    for post in posts:
        for comment in post["comments"]:
            if comment is None:
                post["comments"].remove(comment)

    return JsonResponse(posts, safe=False, status=200)


@login_required
def profile(request: HttpRequest):
    if request.method == "GET":
        return JsonResponse(request.user.to_json(), status=200)  # type: ignore
    else:
        return JsonResponse({"error": "GET request required"}, status=400)


@login_required
def follow(request: HttpRequest):
    if request.method == "POST" and request.body:
        try:
            data_cleaned = GetUsername.parse_raw(request.body).dict()
        except PydanticValidationError as e:
            message = ", ".join(
                [f"{error['loc']}: {error['msg']}" for error in json.loads(e.json())]
            )
            return JsonResponse({"error": message}, status=400)

        profile_user = User.objects.get(username=data_cleaned["username"])

        if profile_user in request.user.following.all():  # type: ignore
            request.user.following.remove(profile_user)  # type: ignore
            return JsonResponse(
                {"message": f"Unfollowed {profile_user.username}."}, status=200
            )
        else:
            request.user.following.add(profile_user)  # type: ignore
            return JsonResponse(
                {"message": f"You are now following {profile_user.username}."}, status=200
            )

    else:
        return JsonResponse({"error": "POST request required"}, status=400)


@login_required
def following_posts(request: HttpRequest):
    posts = Post.objects.filter(user__in=request.user.following.all())  # type: ignore
    return JsonResponse([post.to_json() for post in posts], safe=False, status=200)
