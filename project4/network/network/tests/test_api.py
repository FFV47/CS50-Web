import pytest
from django.test import TestCase
from django.urls import reverse
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


class APITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(  # type: ignore
            username="user1", password="password", email="user1@email.com"
        )
        cls.user2 = User.objects.create_user(  # type: ignore
            username="user2", password="password", email="user2@email.com"
        )

        # Each user has 1 post
        cls.post1 = Post.objects.create(user=cls.user1, text="post 1")
        cls.post2 = Post.objects.create(user=cls.user2, text="post 2")

        # Post 1 from user1 has 3 comments, in which one is a reply to another comment
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

        # Post 2 from user2 has 1 comment
        cls.comment2 = Comment.objects.create(
            post=cls.post2, user=cls.user2, text="comment 1"
        )

    def test_all_posts(self):
        """
        Test if all posts from the database are returned
        """
        new_posts = []
        for i in range(20):
            new_posts.append(Post(user=self.user1, text=f"post {2 + i}"))

        Post.objects.bulk_create(new_posts)

        # First Page
        url = reverse("network:api:all_posts", args=[1])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        json_resp = response.json()

        self.assertEqual(json_resp["numPages"], 3)
        self.assertEqual(json_resp["nextPage"], 2)
        self.assertEqual(json_resp["previousPage"], None)
        self.assertEqual(len(json_resp["posts"]), 10)

        # Second Page
        url = reverse("network:api:all_posts", args=[2])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        json_resp = response.json()

        self.assertEqual(json_resp["numPages"], 3)
        self.assertEqual(json_resp["nextPage"], 3)
        self.assertEqual(json_resp["previousPage"], 1)
        self.assertEqual(len(json_resp["posts"]), 10)

    def test_user_posts(self):
        """
        Test if all posts from one user are returned, when user is
        logged in
        """
        url = reverse("network:api:user_posts", args=[1])

        response = self.client.post(
            url, {"username": self.user1.username}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)

        self.assertEqual(
            response.json()["detail"],
            "Unauthorized",
        )

        self.client.login(username="user1", password="password")
        url = reverse("network:api:user_posts", args=[1])
        response = self.client.post(
            url, {"username": self.user1.username}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        json_resp = response.json()

        self.assertEqual(json_resp["nextPage"], None)
        self.assertEqual(json_resp["previousPage"], None)
        self.assertEqual(len(json_resp["posts"]), 1)

    def test_profile_route(self):
        url = reverse("network:api:profile", args=["user1"])
        self.client.login(username="user1", password="password")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        resp_json = response.json()

        print(resp_json)

        # raise Exception("")

    def test_following_posts(self):

        self.client.login(username="user1", password="password")

        url = reverse("network:api:follow")
        response = self.client.post(
            url, {"username": "user2"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        url = reverse("network:api:following_posts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertIn(self.user2.username, resp_json[0]["username"])
        self.assertIn(self.post2.text, resp_json[0]["text"])

    def test_new_post(self):
        """
        Test if a new post was published
        """
        self.client.login(username="user1", password="password")
        url = reverse("network:api:new_post")

        response = self.client.post(
            url, {"text": "Hello World"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.posts.count(), 2)

        resp_json = response.json()

        self.assertEqual(resp_json["id"], 3)
        self.assertEqual(resp_json["text"], "Hello World")
        self.assertEqual(resp_json["edited"], False)
        self.assertEqual(resp_json["username"], "user1")
        self.assertEqual(resp_json["likes"], 1)
        self.assertListEqual(resp_json["comments"], [])

    def test_new_post_length(self):
        """
        Test if a new post respects min and max characters.
        """
        self.client.login(username="user1", password="password")
        url = reverse("network:api:new_post")

        # max_length test
        response = self.client.post(
            url,
            {"text": "a" * 300},
            content_type="application/json",
        )

        error = response.json()["errors"][0]

        self.assertEqual(response.status_code, 400)
        self.assertEqual(error["msg"], "Post must be at most 280 characters long.")

        # min_length test
        response = self.client.post(url, {"text": "a"}, content_type="application/json")
        error = response.json()["errors"][0]

        self.assertEqual(response.status_code, 400)
        self.assertEqual(error["msg"], "Post must be at least 5 characters long.")

        self.assertEqual(self.user1.posts.count(), 1)
        self.assertEqual(Post.objects.count(), 2)

    def test_post_likes(self):

        self.client.login(username="user1", password="password")

        url = reverse("network:api:like_post", args=[self.post1.id])
        print(url)
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 200)

        # like post
        resp_json = response.json()
        self.assertEqual(resp_json["id"], self.post1.id)
        self.assertEqual(resp_json["likes"], 1)
        self.assertEqual(resp_json["likedByUser"], True)
        self.assertIn(self.user1, self.post1.liked_by.all())

        response = self.client.patch(url)

        # unlike post
        resp_json = response.json()
        self.assertEqual(resp_json["id"], self.post1.id)
        self.assertEqual(resp_json["likes"], 0)
        self.assertEqual(resp_json["likedByUser"], False)
        self.assertNotIn(self.user1, self.post1.liked_by.all())

    def test_new_comment(self):
        """
        Test if a new comment was published on the correct post
        """
        self.client.login(username="user1", password="password")

        url = reverse("network:api:new_comment")

        response = self.client.post(
            url,
            {"text": "Hello World", "postID": self.post1.id},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.comments.count(), 4)

        # Returns Post object
        resp_json = response.json()

        # Post 1 has 2 comments that are not replies
        self.assertEqual(resp_json["id"], 1)
        self.assertEqual(resp_json["text"], "post 1")
        self.assertEqual(resp_json["edited"], False)
        self.assertEqual(resp_json["username"], "user1")
        self.assertEqual(resp_json["likes"], 0)
        self.assertEqual(resp_json["likedByUser"], False)
        self.assertEqual(len(resp_json["comments"]), 3)

        # In total there were 4 comments (Post 2 has 1 comment)
        # The first comment must be the new one
        self.assertEqual(resp_json["comments"][0]["id"], 5)
        self.assertEqual(resp_json["comments"][0]["text"], "Hello World")
        self.assertEqual(resp_json["comments"][0]["username"], "user1")
        # self.assertEqual(
        #     resp_json["comments"][0]["publicationDate"], format_date(timezone.now())
        # )
        self.assertListEqual(resp_json["comments"][0]["replies"], [])

    def test_follow_user(self):
        self.client.login(username="user1", password="password")

        url = reverse("network:api:follow")

        response = self.client.post(
            url, {"username": "user2"}, content_type="application/json"
        )
        print(response.json())
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.user2, self.user1.following.all())
        self.assertIn(self.user1, self.user2.followers.all())

        resp_json = response.json()
        self.assertEqual(
            resp_json["message"], f"You are now following {self.user2.username}"
        )
        self.assertEqual(resp_json["isFollowing"], True)

        self.assertNotIn(self.user2, self.user1.followers.all())

        response = self.client.post(
            url, {"username": "user2"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        self.assertNotIn(self.user2, self.user1.following.all())
        self.assertNotIn(self.user1, self.user2.followers.all())

        resp_json = response.json()
        self.assertEqual(
            resp_json["message"], f"You are no longer following {self.user2.username}"
        )
        self.assertEqual(resp_json["isFollowing"], False)
