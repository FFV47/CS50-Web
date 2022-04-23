from os import path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


# IMAGE VALIDATOR
def file_ext(image):
    extension = image.name.split(".")[-1]
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(_("Only JPEG and PNG images allowed."), code="wrong_ext")


# IMAGE VALIDATOR
def file_size(image):
    limit = 2.5 * 1024 * 1024
    if image.size > limit:
        raise ValidationError(
            _("Image file too large. Size should not exceed 2.5 MB."), code="big_file"
        )


# file will be uploaded to MEDIA_ROOT/user_<id>/<random_filename>
def upload_path(instance, filename):
    file_ext = path.splitext(filename)[1]
    return f"auctions/user_{instance.vendor.id}/{uuid4().hex}{file_ext}"
