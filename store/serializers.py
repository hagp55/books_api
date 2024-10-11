from django.contrib.auth.models import User
from rest_framework import serializers

from store.models import Book, UserBookRelation


class BookReaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
        )


class BookSerializer(serializers.ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
        read_only=True,
    )
    owner_name = serializers.CharField(
        source="owner.username", default="not owner", read_only=True
    )
    readers = BookReaderSerializer(many=True, read_only=True)
    # likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id",
            "name",
            "price",
            "author_name",
            "annotated_likes",
            "rating",
            "owner_name",
            "readers",
            # "likes_count",
        )

    # def get_likes_count(self, obj):
    #     return UserBookRelation.objects.filter(book=obj, like=True).count()


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ["book", "like", "in_bookmarks", "rating"]
