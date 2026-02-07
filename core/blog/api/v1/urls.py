from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostModelViewSet

app_name = "api-v1"

router = DefaultRouter()
router.register("posts", PostModelViewSet, basename="post")


urlpatterns = [
    path("", include(router.urls)),
]