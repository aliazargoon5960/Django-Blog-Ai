from django.db import models
from accounts.models.profiles import Profile
from django.utils.text import slugify
from .category import Category
from .tag import Tag
from django.utils import timezone

class Post(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"

    author = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="posts")

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField()
    image = models.ImageField(upload_to="blog/post", null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True,related_name="posts")

    tags = models.ManyToManyField(Tag , blank=True, related_name="posts")

    status = models.CharField(max_length=10,choices=Status.choices,default=Status.DRAFT)

    view_count = models.PositiveIntegerField(default=0)

    is_ai_generated = models.BooleanField(default=False)
    voice_file = models.FileField(upload_to="blog/voice", null=True, blank=True)

    published_date = models.DateTimeField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        if self.status == self.Status.PUBLISHED and not self.published_date:
            self.published_date = timezone.now()

        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
