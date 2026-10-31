from django.urls import include, path
from rest_framework import routers

from posts.views import FeedView, PostViewSet

router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="post")

urlpatterns = [
    path("feed/", FeedView.as_view(), name="feed"),
    path("", include(router.urls)),
]
