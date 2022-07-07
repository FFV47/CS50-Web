import magic
from os import path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat


app_name = path.basename(path.dirname(__file__))


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


# https://docs.djangoproject.com/en/4.0/ref/validators/
# You can also use a class with a __call__() method for more complex
# or configurable validators. RegexValidator, for example, uses this
# technique. If a class-based validator is used in the validators
# model field option, you should make sure it is serializable by the
# migration framework by adding deconstruct() and __eq__() methods.
@deconstructible
class FileValidator:
    error_messages = {
        "max_size": _(
            "File size must not be greater than %(max_size)s. Your file size is %(size)s."
        ),
        "min_size": _(
            "File size must not be less than %(min_size)s. Your file size is %(size)s."
        ),
        "content_type": _("File of type %(content_type)s are not supported."),
    }

    def __init__(self, max_size=None, min_size=None, content_types=None):
        self.max_size = max_size * 1024 * 1024 if max_size is not None else None
        self.min_size = min_size * 1024 * 1024 if min_size is not None else None
        self.content_types = content_types

    def __call__(self, file):
        if self.max_size is not None and file.size > self.max_size:
            params = {
                "max_size": filesizeformat(self.max_size),
                "size": filesizeformat(file.size),
            }
            raise ValidationError(
                message=self.error_messages["max_size"],
                code="max_size",
                params=params,
            )

        if self.min_size is not None and file.size < self.min_size:
            params = {
                "min_size": filesizeformat(self.min_size),
                "size": filesizeformat(file.size),
            }
            raise ValidationError(
                message=self.error_messages["min_size"], code="min_size", params=params
            )

        if self.content_types is not None:
            content_type = magic.from_buffer(file.read(), mime=True)
            file.seek(0)

            if content_type not in self.content_types:
                params = {"content_type": content_type}
                raise ValidationError(
                    message=self.error_messages["content_type"],
                    code="content_type",
                    params=params,
                )

        return file

    def __eq__(self, other):
        return (
            isinstance(other, FileValidator)
            and self.max_size == other.max_size
            and self.min_size == other.min_size
            and self.content_types == other.content_types
        )
