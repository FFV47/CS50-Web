import pytest
from django.forms import ValidationError
from django.test import TestCase
from django.utils import timezone

from network.models import Comment, Post, User


def format_date(datetime: timezone.datetime):
    return timezone.localtime(datetime).strftime("%B %d, %Y - %H:%M")


@pytest.fixture(autouse=True)
def whitenoise_autorefresh(settings):
    """
    Get rid of whitenoise "No directory at" warning, as it's not helpful when running tests.

    Related:
        - https://github.com/evansd/whitenoise/issues/215
        - https://github.com/evansd/whitenoise/issues/191
        - https://github.com/evansd/whitenoise/commit/4204494d44213f7a51229de8bc224cf6d84c01eb
    """
    settings.WHITENOISE_AUTOREFRESH = True


# Create your tests here.
class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(  # type: ignore
            username="user1", password="password", email="user1@email.com"
        )
        cls.user2 = User.objects.create_user(  # type: ignore
            username="user2", password="password", email="user2@email.com"
        )

        cls.post1 = Post.objects.create(user=cls.user1, text="post 1")
        cls.post2 = Post.objects.create(user=cls.user2, text="post 2")

        cls.comment1 = Comment.objects.create(
            post=cls.post1, user=cls.user1, text="comment 1"
        )
        cls.comment_child = Comment.objects.create(
            post=cls.post1,
            user=cls.user1,
            text="child comment",
            parent_comment=cls.comment1,
        )

        Comment.objects.create(post=cls.post1, user=cls.user1, text="comment 2")

        cls.comment2 = Comment.objects.create(
            post=cls.post2, user=cls.user2, text="comment 1"
        )

    def test_users_posts(self):
        self.assertIn(self.post1, self.user1.posts.all())
        self.assertIn(self.post2, self.user2.posts.all())

    def test_comments_in_posts(self):
        self.assertIn(self.comment1, self.post1.comments.all())
        self.assertNotIn(self.comment1, self.post2.comments.all())
        self.assertIn(self.comment2, self.post2.comments.all())
        self.assertNotIn(self.comment2, self.post1.comments.all())

    def test_child_comment(self):
        self.assertIn(self.comment_child, self.comment1.replies.all())

    def test_child_comment_not_in_parent_post(self):
        self.assertIn(self.comment_child, self.post1.comments.filter(reply=True))
        self.assertNotIn(self.comment_child, self.post1.comments.filter(reply=False))

    def test_child_comment_in_same_post_as_parent(self):

        comment1 = Comment.objects.create(
            user=self.user1, text="comment 1", post=self.post1
        )
        reply_comment1 = Comment(
            user=self.user1,
            post=self.post2,
            text="wrong reply comment 1",
            parent_comment=comment1,
        )

        self.assertRaises(ValidationError, reply_comment1.save)
