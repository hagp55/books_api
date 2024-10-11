import json

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Case, Count, When
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )
        self.book1 = Book.objects.create(
            name="Test book 1",
            price="25",
            author_name="Author 1",
            owner=self.user,
        )
        self.book2 = Book.objects.create(
            name="Test book 2",
            price="55",
            author_name="Author 5",
        )
        self.book3 = Book.objects.create(
            name="Test book 3 Author 1",
            price="55",
            author_name="Author 2",
        )
        UserBookRelation.objects.create(
            user=self.user,
            book=self.book1,
            like=True,
            rating=5,
        )

    def test_get_books(self) -> None:
        url = reverse("book-list")
        with CaptureQueriesContext(connection=connection) as queries:
            response = self.client.get(url)
            self.assertEqual(len(queries), 2)

            books = (
                Book.objects.all()
                .annotate(
                    annotated_likes=Count(Case(When(books__like=True, then=1))),
                    # rating=Avg("books__rating"),
                )
                .order_by("id")
            )
            serializer_data = BookSerializer(
                books,
                many=True,
            ).data
            self.assertEqual(serializer_data, response.data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(serializer_data[0]["annotated_likes"], 1)

    def test_get_books_by_filter(self) -> None:
        url = reverse("book-list")
        response = self.client.get(url, data={"price": 55})
        books = (
            Book.objects.filter(id__in=[self.book2.id, self.book3.id])
            .annotate(
                annotated_likes=Count(Case(When(books__like=True, then=1))),
                # rating=Avg("books__rating"),
            )
            .order_by("id")
        )
        serializer_data = BookSerializer(
            books,
            many=True,
        ).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_books_by_search(self) -> None:
        url = reverse("book-list")
        response = self.client.get(url, data={"search": "Author 1"})
        books = Book.objects.filter(id__in=[self.book1.id, self.book3.id]).annotate(
            annotated_likes=Count(Case(When(books__like=True, then=1))),
        )
        serializer_data = BookSerializer(
            books,
            many=True,
        ).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book(self) -> None:
        self.assertEqual(Book.objects.count(), 3)

        url = reverse("book-list")
        data = dict(
            name="Test book 1",
            price="25",
            author_name="Author 1",
        )
        self.client.force_login(self.user)
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 4)
        self.assertEqual(Book.objects.last().owner, self.user)

    def test_update_book(self) -> None:
        url = reverse("book-detail", args=(self.book1.id,))
        data = dict(
            name=self.book1.name,
            price="575.00",
            author_name=self.book1.author_name,
        )
        self.client.force_login(self.user)
        response = self.client.put(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.book1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["price"], "575.00")

    def test_update_book_without_permissions(self) -> None:
        user2 = User.objects.create_user(username="test_user 2")
        url = reverse("book-detail", args=(self.book1.id,))
        data = dict(
            name=self.book1.name,
            price="575.00",
            author_name=self.book1.author_name,
        )
        self.client.force_login(user2)
        response = self.client.put(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.book1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.book1.price, 25)
        self.assertEqual(
            response.data["detail"],
            "You do not have permission to perform this action.",
        )

    def test_update_book_with_staff_permissions(self) -> None:
        user2 = User.objects.create_user(username="test_user 2", is_staff=True)
        url = reverse("book-detail", args=(self.book1.id,))
        data = dict(
            name=self.book1.name,
            price="575.00",
            author_name=self.book1.author_name,
        )
        self.client.force_login(user2)
        response = self.client.put(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.book1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book1.price, 575)


class BooksRelationApiTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user 1", password="test_password"
        )
        self.user2 = User.objects.create_user(
            username="user 2", password="test_password"
        )
        self.book1 = Book.objects.create(
            name="Test book 1",
            price="25",
            author_name="Author 1",
            owner=self.user1,
        )
        self.book2 = Book.objects.create(
            name="Test book 2", price="55", author_name="Author 5"
        )

    def test_make_like(self) -> None:
        url = reverse("userbookrelation-detail", args=(self.book1.id,))
        data = dict(
            like=True,
        )
        self.client.force_login(self.user1)
        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )
        relation: UserBookRelation = UserBookRelation.objects.get(
            user=self.user1,
            book=self.book1,
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relation.like)

    def test_make_bookmark(self) -> None:
        url = reverse("userbookrelation-detail", args=(self.book1.id,))
        data = dict(
            like=True,
            in_bookmarks=True,
        )
        self.client.force_login(self.user1)
        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )
        relation: UserBookRelation = UserBookRelation.objects.get(
            user=self.user1,
            book=self.book1,
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relation.like)
        self.assertTrue(relation.in_bookmarks)

    def test_make_rate(self) -> None:
        url = reverse("userbookrelation-detail", args=(self.book1.id,))
        data = dict(
            like=True,
            in_bookmarks=True,
            rating=3,
        )
        self.client.force_login(self.user1)
        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )
        relation: UserBookRelation = UserBookRelation.objects.get(
            user=self.user1,
            book=self.book1,
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(relation.like)
        self.assertTrue(relation.in_bookmarks)
        self.assertEqual(relation.rating, 3)

    def test_make_invalid_rate(self) -> None:
        url = reverse("userbookrelation-detail", args=(self.book1.id,))
        data = dict(
            like=True,
            in_bookmarks=True,
            rating=20,
        )
        self.client.force_login(self.user1)
        response = self.client.patch(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(
            status.HTTP_400_BAD_REQUEST,
            response.status_code,
            response.data,
        )
