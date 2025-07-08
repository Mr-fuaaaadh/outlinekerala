from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField


# Custom user model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('reader', 'Reader'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super().save(*args, **kwargs)

# Category model
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    def __str__(self):
        return self.name
    


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)

    def __str__(self):
        return self.name
    




class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    


class News(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)  
    content = RichTextField(config_name='default')
    image = models.ImageField(upload_to='news/')
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='news')
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    publish_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publish_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            counter = 1
            while News.objects.filter(slug=unique_slug).exists():
                suffix = f"-{counter}"
                unique_slug = f"{base_slug[:255 - len(suffix)]}{suffix}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



# Comment model
class Comment(models.Model):
    news = models.ForeignKey(News, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.news.title}"


class Like(models.Model):
    news = models.ForeignKey(News, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('news', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.news.title}"