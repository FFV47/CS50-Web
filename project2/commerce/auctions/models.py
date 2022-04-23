from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# Module for uploaded images
# from .utility import upload_path, file_size, file_ext


class Category(models.Model):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=250)
    pub_date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    # image = models.ImageField(
    #     blank=True, null=True, upload_to=upload_path, validators=[file_size, file_ext]
    # )
    image = models.URLField(max_length=255, blank=True, null=True)
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="catalog"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    bidders = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="Bid", through_fields=("listing", "user"),
    )

    def __str__(self) -> str:
        return f"{self.title}/Price = ${self.price}"


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.CharField(max_length=250)
    post_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author}"


class Bid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    value = models.DecimalField(null=True, max_digits=9, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.user}/Bid = ${self.value}"


class User(AbstractUser):
    watchlist = models.ManyToManyField(Listing, related_name="watchers")
