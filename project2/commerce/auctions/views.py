from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from .forms import BidForm, CommentForm, EditForm, ListingForm
from .models import Bid, Category, Listing, User


def index(request: HttpRequest):
    listings = Listing.objects.filter(active=True).order_by("-id")
    return render(request, "auctions/index.html", {"listings": listings})


# * AUTHENTICATION
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user:
            login(request, user)
            return redirect("auctions:index")
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )

    return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect("auctions:index")


def register(request: HttpRequest):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure password matches confirmation
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return redirect("auctions:index")

    return render(request, "auctions/register.html")


def user_listings(request, user_id):
    return render(
        request,
        "auctions/user_listings.html",
        {
            "user_id": user_id,
            "user_listings": User.objects.get(pk=user_id).catalog.all(),
        },
    )


# * CATEGORIES
def categories(request):
    template_rows = 5
    return render(
        request,
        "auctions/categories.html",
        {"rows": template_rows, "categories": Category.objects.all()},
    )


def category_listing(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = category.listing_set.filter(active=True).order_by("-id")

    return render(
        request,
        "auctions/category_listings.html",
        {"name": category.name, "listings": listings},
    )


# * WATCHLIST
@require_POST
def watch(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watch = int(request.POST["watch"])

    if watch:
        request.user.watchlist.add(listing)
    else:
        request.user.watchlist.remove(listing)

    return redirect("auctions:detail_listing", listing_id)


@login_required
def watchlist(request, listing_id=None):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        request.user.watchlist.remove(listing)
        return redirect("auctions:watchlist")

    return render(
        request, "auctions/watchlist.html", {"watchlist": request.user.watchlist.all()}
    )


# * LISTING MANAGEMENT
def detail_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    comments = listing.comments.all()

    # If there is no bids on the listing, IndexError will be raised
    try:
        highest_bid = listing.bid_set.order_by("-value")[0]
        match_bidder = highest_bid.user == request.user
    except IndexError:
        match_bidder = False

    bid_form = BidForm()
    comment_form = CommentForm()

    return render(
        request,
        "auctions/detail_listing.html",
        {
            "bid_form": bid_form,
            "comments": comments,
            "comment_form": comment_form,
            "listing": listing,
            "match_bidder": match_bidder,
        },
    )


@require_POST
def comment_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.listing = listing
        comment.save()
        return redirect("auctions:detail_listing", listing_id)

    try:
        highest_bid = listing.bid_set.order_by("-value")[0]
        match_bidder = highest_bid.user == request.user
    except IndexError:
        match_bidder = False

    return render(
        request,
        "auctions/detail_listing.html",
        {
            "bid_form": BidForm(),
            "comments": listing.comments.all(),
            "comment_form": form,
            "listing": listing,
            "match_bidder": match_bidder,
        },
    )


@require_POST
def bid_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    # Check listing for any biddings
    try:
        highest_bid = listing.bid_set.order_by("-value")[0]
        match_bidder = highest_bid.user == request.user
    except IndexError:
        highest_bid = False
        match_bidder = False

    value = float(request.POST["value"])
    form = BidForm(request.POST)

    # Check if input value is higher than current bid on active listing
    if form.is_valid() and value > listing.price and listing.active:
        bid = Bid.objects.get_or_create(user=request.user, listing=listing)[0]
        bid.value = form.cleaned_data["value"]
        listing.price = form.cleaned_data["value"]
        listing.save()
        bid.save()
        return redirect("auctions:detail_listing", listing_id)

    # Block biddings on closed listing
    elif not listing.active and highest_bid:
        closed = ValidationError(
            _("This listing is closed.\n%(winner)s won the auction."),
            code="closed",
            params={"winner": highest_bid.user},
        )
        form.add_error(field="value", error=closed)

    else:
        bid_lower = ValidationError(
            _("Bid must be higher than $%(price)s"),
            code="bid_lower",
            params={"price": listing.price},
        )
        form.add_error(field="value", error=bid_lower)

    return render(
        request,
        "auctions/detail_listing.html",
        {
            "bid_form": form,
            "comments": listing.comments.all(),
            "comment_form": CommentForm(),
            "listing": listing,
            "match_bidder": match_bidder,
        },
    )


@login_required
def new_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            # Retrieve Model from the Form without committing to database
            listing = form.save(commit=False)
            listing.vendor = request.user
            listing.save()
            # After registering the user as the vendor, ManyToMany Field needs to be saved manually if commit=False
            form.save_m2m()
            return redirect("auctions:index")
        else:
            return render(request, "auctions/new_listing.html", {"form": form})

    form = ListingForm()
    return render(request, "auctions/new_listing.html", {"form": form})


@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == "POST":
        form = EditForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            return redirect("auctions:index")
        else:
            # listing is updated with request.POST data in form.is_valid()
            # even if the form is not valid, so the object must be repopulated from the DB
            listing.refresh_from_db()
            return render(
                request,
                "auctions/edit_listing.html",
                {"form": form, "listing": listing},
            )

    form = EditForm(instance=listing)
    return render(
        request, "auctions/edit_listing.html", {"form": form, "listing": listing}
    )


@login_required
def close_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    listing.active = False
    listing.save()

    # Check listing for biddings
    try:
        winner = listing.bid_set.order_by("-value")[0].user
    except IndexError:
        winner = False

    # Add listing to winner's watchlist
    if winner and listing not in winner.watchlist.all():
        winner.watchlist.add(listing)

    return redirect("auctions:detail_listing", listing_id)


@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    listing.delete()
    return redirect("auctions:user_listings", request.user.id)
