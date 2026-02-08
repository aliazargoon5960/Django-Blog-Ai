from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import F
from blog.models import Post
from .serializers import PostSerializer
from .permissions import IsAdminOrReadOnly
from .pagination import DefaultPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter



class PostModelViewSet(ModelViewSet):
    queryset = Post.objects.select_related("author__user", "category").prefetch_related("tags", "comments__author__user")
    serializer_class = PostSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'author', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']


    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrReadOnly()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        queryset = super().get_queryset()

        
        if not self.request.user.is_authenticated or self.request.user.role != "ADMIN":
            queryset = queryset.filter(status=Post.Status.PUBLISHED)

        return queryset

    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count = F("view_count") + 1
        instance.save(update_fields=["view_count"])
        instance.refresh_from_db()
        return super().retrieve(request, *args, **kwargs)

    

