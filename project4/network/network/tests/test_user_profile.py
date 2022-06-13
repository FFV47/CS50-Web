import pytest
from django.test import TestCase
from django.utils import timezone
from network.models import User


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


class UserProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(  # type: ignore
            username="user1", password="password", email="user1@email.com"
        )

        cls.user2 = User.objects.create_user(  # type: ignore
            username="user2", password="password", email="user2@email.com"
        )

        cls.user3 = User.objects.create_user(  # type: ignore
            username="user3", password="password", email="user3@email.com"
        )

    def test_user_cant_follow_himself(self):
        self.user1.following.add(self.user1)
        self.user1.followers.add(self.user1)

        self.assertNotIn(self.user1, self.user1.following.all())
        self.assertNotIn(self.user1, self.user1.followers.all())

    def test_user_following_relationship(self):
        """
        Test if user2 and user3 are in user1 followers list,
        user1 in user2 and user3 following list,
        user1 are not in user2 and user3 followers list
        """

        self.user1.followers.add(self.user2, self.user3)

        self.assertListEqual([self.user2, self.user3], list(self.user1.followers.all()))
        self.assertNotIn(self.user2, self.user1.following.all())
        self.assertNotIn(self.user3, self.user1.following.all())

        # user2 and user3 must be following user 1
        self.assertIn(self.user1, self.user2.following.all())
        self.assertNotIn(self.user1, self.user2.followers.all())
        self.assertIn(self.user1, self.user3.following.all())
        self.assertNotIn(self.user1, self.user3.followers.all())
