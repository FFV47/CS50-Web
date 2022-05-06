from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
from django.http import HttpRequest
from django.shortcuts import redirect, render

from .models import User


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
        return render(request, "network/login.html", {"page": "login"})


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
                request,
                "network/register.html",
                {"message": "Passwords must match.", "page": "register"},
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
            return render(
                request,
                "network/register.html",
                {"message": messages, "page": "register"},
            )

        login(request, user)
        return redirect("network:index")
    else:
        return render(request, "network/register.html", {"page": "register"})
