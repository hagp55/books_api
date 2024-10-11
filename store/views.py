from django.db.models import Case, Count, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrStaffOrReadOnly
from store.serializers import BookSerializer, UserBookRelationSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = (
        Book.objects.all()
        .annotate(annotated_likes=Count(Case(When(books__like=True, then=1))))
        .select_related("owner")
        .prefetch_related("readers")
        .order_by("id")
    )
    serializer_class = BookSerializer
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ("price",)
    search_fields = ("author_name", "name")
    ordering_fields = ("price", "author_name")

    def perform_create(self, serializer) -> None:
        user = self.request.user
        serializer.save(owner=user)


class UserBookRelationalView(
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "book"
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(
            user=self.request.user, book_id=self.kwargs["book"]
        )
        return obj
