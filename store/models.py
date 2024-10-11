from django.db import models


class Book(models.Model):
    """
    A model representing a book with a name, price, author name, owner, readers, and rating.

    Attributes:
        name (models.CharField): The name of the book.
        price (models.DecimalField): The price of the book.
        author_name (models.CharField): The name of the author of the book.
        owner (models.ForeignKey): The owner of the book.
        readers (models.ManyToManyField): The readers of the book.
        rating (models.DecimalField): The rating of the book.

    Methods:
        __str__: Returns a string representation of the book.
    """

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        related_name="owner_books",
        null=True,
    )
    readers = models.ManyToManyField(
        "auth.User",
        through="UserBookRelation",
        related_name="reader_books",
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        default=None,
    )

    def __str__(self):
        return f"Name={self.name} with Price={self.price}"


class UserBookRelation(models.Model):
    """
    A model representing a relation between a user and a book with a like, bookmark, and rating.

    Attributes:
        user (models.ForeignKey): The user who has the relation with the book.
        book (models.ForeignKey): The book that the user has the relation with.
        like (models.BooleanField): Whether the user likes the book.
        in_bookmarks (models.BooleanField): Whether the book is in the user's bookmarks.
        rating (models.PositiveSmallIntegerField): The rating of the book by the user.

    Methods:
        __str__: Returns a string representation of the relation.
        __save__: Saves the relation and sets the rating of the book.
    """

    RATE_CHOICES = (
        (1, "Ok"),
        (2, "Fine"),
        (3, "Good"),
        (4, "Great"),
        (5, "Awesome"),
    )
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="user_books",
    )
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="books",
    )
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        """
        Returns a string representation of the relation.

        Returns:
            str: A string representation of the relation.
        """
        return f"{self.user.username} liked {self.book.name} rating {self.rating}"

    def __save__(self, *args, **kwargs):
        """
        Saves the relation and sets the rating of the book.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        from store.logic import set_rating

        creating = not self.pk
        old_rating = self.book.rating
        super().save(*args, **kwargs)

        new_rating = self.book.rating
        if old_rating != new_rating or creating:
            set_rating(self.book)
