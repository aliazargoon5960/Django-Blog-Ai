from django.contrib import admin
from .models import Post, Category, Tag
from django.utils import timezone


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "is_active", "created_date"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "created_date"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = ["title", "author", "status", "view_count", "published_date", "created_date"]

    list_filter = ["status", "created_date", "category", "tags"]
    search_fields = ["title", "description", "author__user__email"]

    prepopulated_fields = {"slug": ("title",)}

    readonly_fields = ["view_count", "published_date", "created_date", "updated_date"]

    filter_horizontal = ["tags"]

    date_hierarchy = "created_date"

    actions = ["make_published"]

    
    @admin.action(description="Publish selected posts")
    def make_published(self, request, queryset):
        updated = queryset.update(status=Post.Status.PUBLISHED, published_date=timezone.now())
        self.message_user(request, f"{updated} post(s) successfully published.")