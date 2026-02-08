from rest_framework import serializers
from ...models import Post , Category , Tag
from accounts.models import Profile
from django.urls import reverse
from comments.api.v1.serializers import CommentSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", 'parent']



class PostSerializer(serializers.ModelSerializer):
    snippet = serializers.ReadOnlyField(source='get_snippet')
    absolute_url = serializers.SerializerMethodField(method_name="get_abs_url")
    comments = serializers.SerializerMethodField(method_name="get_comments")
    class Meta:
        model = Post
        fields = ["id", "title", "author", "snippet" ,"description", "category", "tags", "image", "view_count","absolute_url", "comments", "published_date"]
        read_only_fields = ["author", "view_count"]

    
    def get_abs_url(self,obj):
        request = self.context.get('request')
        relative_url = reverse('blog:api-v1:post-detail', args=[obj.pk])
        return request.build_absolute_uri(relative_url)

    
    def to_representation(self, instance):
        request = self.context.get('request')
        rep = super().to_representation(instance)
        if request.parser_context.get('kwargs').get('pk'):
            rep.pop('snippet', None)
            rep.pop('absolute_url', None)
        else:
            rep.pop('description', None)
            rep.pop('image', None)
            rep.pop('comments', None)


        rep['category'] = CategorySerializer(instance.category).data
        rep['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return rep
    
    def get_comments(self, obj):
        request = self.context.get("request")
        queryset = obj.comments.filter(is_visible=True, parent=None)
        serializer = CommentSerializer(queryset, many=True, context={'request': request})
        return serializer.data

    def create(self, validated_data):
        validated_data['author'] = Profile.objects.get(user__id = self.context.get('request').user.id)
        return super().create(validated_data)


