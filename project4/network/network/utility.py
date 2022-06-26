from os import path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app_name = path.basename(path.dirname(__file__))


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


def upload_path(instance, filename):
    """
    file will be uploaded to MEDIA_ROOT/user_<id>/<random_filename>

    :param instance: An instance of the model where the FileField
    is defined. More specifically, this is the particular instance
    where the current file is being attached. In most cases, this
    object will not have been saved to the database yet, so if it uses
    the default AutoField, it might not yet have a value for its
    primary key field.

    :param filename: The filename that was originally given to the
    file. This may or may not be taken into account when determining
    the final destination path.
    """
    file_ext = path.splitext(filename)[1]
    return f"{app_name}/user_{instance.id}/{uuid4().hex}{file_ext}"
