from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from .models import User, Post, Comment


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


class ViewsAPITest(TestCase):
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
        url = reverse("network:all_posts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_user_posts(self):
        """
        Test if all posts from one user are returned, when user is
        loggeg in
        """
        url = reverse("network:all_posts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

        response = self.client.post(
            url, {"username": self.user1.username}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"], "GET or POST with authentication request required"
        )

        self.client.login(username="user1", password="password")
        url = reverse("network:all_posts")
        response = self.client.post(
            url, {"username": self.user1.username}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_following_posts(self):

        self.client.login(username="user1", password="password")

        url = reverse("network:follow")
        response = self.client.post(
            url, {"username": "user2"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        url = reverse("network:following_posts")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        resp_json = response.json()
        self.assertIn(self.user2.username, resp_json[0]["user"])
        self.assertIn(self.post2.text, resp_json[0]["text"])

    def test_user_new_post(self):
        """
        Test if a new post was published
        """
        self.client.login(username="user1", password="password")
        url = reverse("network:new_post")

        response = self.client.post(
            url, {"post_text": "Hello World"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.posts.count(), 2)

        resp_json = response.json()
        self.assertEqual(resp_json["message"], "Post created successfully.")
        self.assertEqual(resp_json["post"]["text"], "Hello World")
        self.assertEqual(resp_json["post"]["user"], self.user1.username)
        self.assertListEqual(resp_json["post"]["liked_by"], [])

    def test_new_post_length(self):
        """
        Test if a new post respects min and max characters.
        """
        self.client.login(username="user1", password="password")
        url = reverse("network:new_post")

        # max_length test
        response = self.client.post(
            url,
            {"post_text": "a" * 300},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"], "Post must be at most 280 characters long."
        )

        # min_length test
        response = self.client.post(
            url, {"post_text": "a"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"], "Post must be at least 5 characters long."
        )

        self.assertEqual(self.user1.posts.count(), 1)
        self.assertEqual(Post.objects.count(), 2)

    def test_post_likes(self):

        self.client.login(username="user1", password="password")

        url = reverse("network:like_post")
        response = self.client.post(
            url, {"post_id": self.post1.id}, content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        # like post
        resp_json = response.json()
        self.assertEqual(resp_json["message"], "Post liked")
        self.assertIn(self.user1.username, resp_json["post"]["liked_by"])

        response = self.client.post(
            url, {"post_id": self.post1.id}, content_type="application/json"
        )
        # unlike post
        resp_json = response.json()
        self.assertEqual(resp_json["message"], "Post unliked")
        self.assertNotIn(self.user1.username, resp_json["post"]["liked_by"])
        self.assertEqual(len(resp_json["post"]["liked_by"]), 0)

    def test_new_comment(self):
        self.client.login(username="user1", password="password")

        url = reverse("network:new_comment")

        response = self.client.post(
            url,
            {"comment_text": "Hello World", "post_id": self.post1.id},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user1.comments.count(), 4)

        resp_json = response.json()
        self.assertEqual(resp_json["message"], "Comment created successfully.")
        self.assertEqual(resp_json["comment"]["text"], "Hello World")
        self.assertEqual(resp_json["comment"]["user"], self.user1.username)

    def test_follow_user(self):
        self.client.login(username="user1", password="password")

        url = reverse("network:follow")

        response = self.client.post(
            url, {"username": "user2"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.user2, self.user1.following.all())
        self.assertIn(self.user1, self.user2.followers.all())

        resp_json = response.json()
        self.assertEqual(
            resp_json["message"], f"You are now following {self.user2.username}."
        )

        self.assertNotIn(self.user2, self.user1.followers.all())

        response = self.client.post(
            url, {"username": "user2"}, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        self.assertNotIn(self.user2, self.user1.following.all())
        self.assertNotIn(self.user1, self.user2.followers.all())

        resp_json = response.json()
        self.assertEqual(resp_json["message"], f"Unfollowed {self.user2.username}.")
