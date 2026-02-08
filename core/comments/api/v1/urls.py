from rest_framework.routers import DefaultRouter
from .views import CommentModelViewSet


app_name = "api-v1"
router = DefaultRouter()
router.register("comments", CommentModelViewSet, basename="comments")

urlpatterns = router.urls
