from network.models import User, Post, Comment
from django.utils import timezone
import json

import datetime

with open("model_fields.json", "w") as f:

    user_fields = [item.name for item in User._meta.get_fields(include_hidden=True)]
    post_fields = [item.name for item in Post._meta.get_fields(include_hidden=True)]
    comment_fields = [item.name for item in Comment._meta.get_fields(include_hidden=True)]
    fields = [user_fields] + [post_fields] + [comment_fields]

    f.write(json.dumps(fields, indent=2))

# django_time = timezone.now()

# print(timezone.now())
# print(timezone.localtime())
# print(datetime.datetime.now())
# print(timezone.datetime.now())
