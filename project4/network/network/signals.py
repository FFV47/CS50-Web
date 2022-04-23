from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import User


@receiver(
    m2m_changed, sender=User.following.through, dispatch_uid="user_following_changed"
)
def block_self_follow(sender, instance, action, **kwargs):
    if action == "post_add":
        if instance in instance.following.all():
            instance.following.remove(instance)
        if instance in instance.followers.all():
            instance.followers.remove(instance)
