import graphene
from graphene_django import DjangoObjectType
from .models import *
from django.conf import settings
from django.core.cache import cache
from promise import Promise
from promise.dataloader import DataLoader

CACHE_TIMEOUT = 300  # 5 minutes

# ------------------ DataLoaders ------------------
class CommentsByNewsLoader(DataLoader):
    def batch_load_fn(self, news_ids):
        qs = Comment.objects.filter(news_id__in=news_ids, approved=True).select_related("user")
        news_map = {news_id: [] for news_id in news_ids}
        for comment in qs:
            news_map[comment.news_id].append(comment)
        return Promise.resolve([news_map[nid] for nid in news_ids])

# ------------------ GraphQL Types ------------------
class UserType(DjangoObjectType):
    profile_picture_url = graphene.String()

    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "role", "bio", "profile_picture")

    def resolve_profile_picture_url(self, info):
        if self.profile_picture:
            return f"{settings.MEDIA_URL}{self.profile_picture}"
        return None

class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")

class CategoryType(DjangoObjectType):
    subcategories = graphene.List(lambda: SubCategoryType)

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "image")

    def resolve_subcategories(self, info):
        cache_key = f"category_{self.id}_subcategories"
        cached = cache.get(cache_key)
        if cached:
            return cached
        qs = list(self.subcategories.all())
        cache.set(cache_key, qs, CACHE_TIMEOUT)
        return qs

class SubCategoryType(DjangoObjectType):
    news = graphene.List(lambda: NewsType)

    class Meta:
        model = SubCategory
        fields = ("id", "name", "slug", "category", "image")

    def resolve_news(self, info):
        cache_key = f"subcategory_{self.id}_news"
        cached = cache.get(cache_key)
        if cached:
            return cached
        qs = list(self.news.all())
        cache.set(cache_key, qs, CACHE_TIMEOUT)
        return qs

class CommentType(DjangoObjectType):
    user = graphene.Field(UserType)

    class Meta:
        model = Comment
        fields = ("id", "content", "approved", "created_at", "user", "parent", "news")

    def resolve_createdAt(self, info):
        return self.created_at


class LikeType(DjangoObjectType):
    user = graphene.Field(UserType)

    class Meta:
        model = Like
        fields = ("id", "user", "news")

class NewsType(DjangoObjectType):
    comments = graphene.List(CommentType)
    likes_count = graphene.Int()
    comments_count = graphene.Int()
    tags = graphene.List(TagType)
    likes = graphene.List(LikeType)  # Add this

    class Meta:
        model = News
        fields = ("id", "title", "slug", "content", "image", "publish_date", "status", "author", "category", "tags", "likes", "comments")


    # ------------------ Resolvers ------------------
    def resolve_comments(self, info):
        # Example fix
        if self.comments is None:
            return []
        return self.comments.all()

    def resolve_likes_count(self, info):
        cache_key = f"news_{self.id}_likes_count"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        count = self.likes.count()
        cache.set(cache_key, count, CACHE_TIMEOUT)
        return count

    def resolve_comments_count(self, info):
        cache_key = f"news_{self.id}_comments_count"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        count = self.comments.filter(approved=True).count()
        cache.set(cache_key, count, CACHE_TIMEOUT)
        return count

    def resolve_tags(self, info):
        cache_key = f"news_{self.id}_tags"
        cached = cache.get(cache_key)
        if cached:
            return cached
        qs = list(self.tags.all())
        cache.set(cache_key, qs, CACHE_TIMEOUT)
        return qs
    
    # Resolver for likes
    def resolve_likes(self, info):
        return self.likes.all()