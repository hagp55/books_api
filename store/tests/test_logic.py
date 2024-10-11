from django.contrib.auth.models import User
from django.test import TestCase

from store.logic import set_rating
from store.models import Book, UserBookRelation


class SetRatingTestCase(TestCase):
    def setUp(self):
        user1 = User.objects.create(
            username="user1",
            first_name="test_first_name",
            last_name="test_last_name",
        )
        user2 = User.objects.create(username="user2")
        user3 = User.objects.create(username="user3")

        self.book1 = Book.objects.create(
            name="Test book 1",
            price="25",
            author_name="Author 1",
            owner=user1,
        )

        UserBookRelation.objects.create(
            user=user1, book=self.book1, like=True, rating=5
        )
        UserBookRelation.objects.create(
            user=user2, book=self.book1, like=True, rating=5
        )
        UserBookRelation.objects.create(
            user=user3, book=self.book1, like=True, rating=4
        )

    def test_set_rating_success(self):
        set_rating(self.book1)
        self.assertEqual(str(Book.objects.get(id=self.book1.id).rating), "4.67")
