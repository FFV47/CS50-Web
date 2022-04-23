import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import JsonResponse, HttpRequest
from django.shortcuts import HttpResponse, redirect, render

# from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email

from .models import User, Email


def index(request: HttpRequest) -> HttpResponse:

    # Authenticated users view their inbox
    if request.user.is_authenticated:
        user = {"email": request.user.email}  # type: ignore
        return render(request, "mail/inbox.html", {"user": user})

    # Everyone else is prompted to sign in
    else:
        return redirect("mail:login")


# @csrf_exempt
@login_required
def compose(request: HttpRequest):

    # Composing a new email must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check recipient emails
    data = json.loads(request.body)
    emails = [email.strip() for email in data.get("recipients").split(",")]
    if emails == [""]:
        return JsonResponse({"error": "At least one recipient required."}, status=400)

    # Convert email addresses to users
    recipients = []
    for email in emails:
        try:
            user = User.objects.get(email=email)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": f"User with email {email} does not exist."}, status=400
            )

    # Get contents of email
    subject = data.get("subject", "")
    body = data.get("body", "")

    # Create one email for each recipient, plus sender
    users = set()
    users.add(request.user)
    users.update(recipients)
    for user in users:
        email = Email(
            user=user,
            sender=request.user,
            subject=subject,
            body=body,
            read=user == request.user,
        )
        email.save()
        for recipient in recipients:
            email.recipients.add(recipient)
        email.save()

    return JsonResponse({"message": "Email sent successfully."}, status=201)


@login_required
def mailbox(request: HttpRequest, mailbox: str):

    # Filter emails returned based on mailbox
    if mailbox == "inbox":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=False
        )
    elif mailbox == "sent":
        emails = Email.objects.filter(user=request.user, sender=request.user)
    elif mailbox == "archive":
        emails = Email.objects.filter(
            user=request.user, recipients=request.user, archived=True
        )
    else:
        return JsonResponse({"error": "Invalid mailbox."}, status=400)

    # Return emails in reverse chronologial order
    emails = emails.order_by("-timestamp")
    return JsonResponse([email.serialize() for email in emails], safe=False)


# @csrf_exempt
@login_required
def email(request: HttpRequest, email_id: int):

    # Query for requested email
    try:
        email = Email.objects.get(user=request.user, pk=email_id)
    except Email.DoesNotExist:
        return JsonResponse({"error": "Email not found."}, status=404)

    # Return email contents
    if request.method == "GET":
        return JsonResponse(email.serialize())

    # Update whether email is read or should be archived
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("read") is not None:
            email.read = data["read"]
        if data.get("archived") is not None:
            email.archived = data["archived"]
        email.save()
        return HttpResponse(status=204)

    # Email must be via GET or PUT
    else:
        return JsonResponse({"error": "GET or PUT request required."}, status=400)


def login_view(request: HttpRequest):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("mail:index")
        else:
            return render(
                request,
                "mail/login.html",
                {"message": "Invalid email and/or password."},
            )
    else:
        return render(request, "mail/login.html")


def logout_view(request: HttpRequest):
    logout(request)
    return redirect("mail:index")


def register(request: HttpRequest):
    if request.method == "POST":
        try:
            email = request.POST["email"]
            validate_email(email)
        except ValidationError as e:
            return render(request, "mail/register.html", {"message": e.message})

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "mail/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)  # type: ignore
            user.save()
        except IntegrityError as e:
            print(e)
            return render(
                request,
                "mail/register.html",
                {"message": "Email address already taken."},
            )
        login(request, user)
        return redirect("mail:index")
    else:
        return render(request, "mail/register.html")
