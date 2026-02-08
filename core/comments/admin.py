from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["id", "short_content", "author", "post", "parent", "is_visible", "ai_checked", "created_date"]

    list_filter = ["is_visible", "ai_checked", "created_date", "post"]

    search_fields = ["content", "author__user__email", "post__title"]

    autocomplete_fields = ["author", "post", "parent"]

    readonly_fields = ["created_date", "updated_date", "ai_checked", "ai_score"]

    ordering = ("-created_date",)

    
    def short_content(self, obj):
        return obj.content[:40]

    short_content.short_description = "content"
