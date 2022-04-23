from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm


# Create your views here.
def index(request):
    print(request.user.is_authenticated)
    if not request.user.is_authenticated:
        return redirect("users:login")
    else:
        return render(request, "users/user.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("users:index")
        form = UserForm()
        return render(
            request,
            "users/login.html",
            {"form": form, "message": "Invalid Credentials!"},
        )
    else:
        form = UserForm()

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    form = UserForm()
    return render(request, "users/login.html", {"form": form, "message": "Logged Out!"})
