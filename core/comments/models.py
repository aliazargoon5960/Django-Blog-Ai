from django.db import models
from django.db import models
from accounts.models import Profile
from blog.models import Post
from django.core.exceptions import ValidationError

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="comments")

    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")

    content = models.TextField()

    # AI moderation
    ai_checked = models.BooleanField(default=False)
    ai_score = models.FloatField(null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_date"]
        indexes = [
        models.Index(fields=["post", "created_date"]),
        models.Index(fields=["parent"]),
        models.Index(fields=["is_visible"]),
    ]

    def clean(self):
        if self.parent and self.parent == self:
            raise ValidationError("Comment cannot be parent of itself")


    def __str__(self):
        return f"{self.author} → {self.post}"
