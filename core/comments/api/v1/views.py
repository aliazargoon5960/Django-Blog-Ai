from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Prefetch
from comments.models import Comment
from .serializers import CommentSerializer
from .permissions import IsOwnerOrAdminOrCreate


class CommentModelViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdminOrCreate]

    def get_queryset(self):
        user = self.request.user

        queryset = Comment.objects.select_related(
            "author__user",
            "post",
            "parent",
        ).prefetch_related("replies")

        if user.is_authenticated and user.role == "ADMIN":
            return queryset


        return queryset.filter(is_visible=True, parent=None)

    def perform_create(self, serializer):
        serializer.save()
