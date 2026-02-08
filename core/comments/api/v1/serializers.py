from rest_framework import serializers
from comments.models import Comment
from accounts.models import Profile


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data



class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.user.email", read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "author_name", "parent", "content", "replies", "created_date"]
        read_only_fields = ["author"]

    
    def get_replies(self, obj):
        depth = self.context.get("depth", 0)

        if depth >= 2:
            return []

        serializer = CommentSerializer(
            obj.replies.filter(is_visible=True),
            many=True,
            context={**self.context, "depth": depth + 1},
        )
        return serializer.data

    
    def create(self, validated_data):
        request = self.context["request"]
        profile = Profile.objects.get(user=request.user)
        validated_data["author"] = profile
        return super().create(validated_data)
