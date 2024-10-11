from django.db.models import Avg

from store.models import UserBookRelation


def set_rating(book):
    """
    Sets the rating of a book.

    Args:
        book: The book to set the rating for.
    """
    rating = (
        UserBookRelation.objects.filter(book=book)
        .aggregate(rating=Avg("rating"))
        .get("rating")
    )
    book.rating = rating
    book.save()
