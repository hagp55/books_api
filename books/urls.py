# from debug_toolbar.toolbar import debug_toolbar_urls
# from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter

from store.views import BookViewSet, UserBookRelationalView

router = SimpleRouter()
router.register(r"book", BookViewSet)
router.register(r"book_relation", UserBookRelationalView)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("social_django.urls", namespace="social")),
    path(
        "home/",
        TemplateView.as_view(
            template_name="index.html",
        ),
    ),
]

urlpatterns += router.urls
# if settings.DEBUG:
#     urlpatterns += debug_toolbar_urls()
