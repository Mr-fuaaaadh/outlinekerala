import graphene
from graphene_django import DjangoObjectType
from .models import *
from .models import CustomUser as User
from django.conf import settings
from django.core.cache import cache
from promise import Promise
from promise.dataloader import DataLoader

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
        model = User
        fields = ("id", "username", "email", "role", "profile_picture", "bio")

    def resolve_profile_picture_url(self, info):
        if self.profile_picture:
            return f"{settings.MEDIA_URL}{self.profile_picture}"
        return None

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "profile_picture")

    def resolve_profile_picture_url(self, info):
        if self.profile_picture:
            return f"{settings.MEDIA_URL}{self.profile_picture}"
        return None

class SubCategoryType(DjangoObjectType):
    class Meta:
        model = SubCategory
        fields = ("id", "name", "slug", "category")

class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")

class CommentType(DjangoObjectType):
    user = graphene.Field(UserType)

    class Meta:
        model = Comment
        fields = ("id", "text", "created_at", "user", "news")

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

    class Meta:
        model = News
        fields = ("id", "title", "slug", "content", "publish_date", "status", "author", "category", "tags")

    # ------------------ Resolvers ------------------
    def resolve_comments(self, info):
        loader = CommentsByNewsLoader()
        return loader.load(self.id)

    def resolve_likes_count(self, info):
        cache_key = f"news_{self.id}_likes_count"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        count = self.likes.count()
        cache.set(cache_key, count, 300)
        return count

    def resolve_comments_count(self, info):
        cache_key = f"news_{self.id}_comments_count"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        count = self.comment_set.filter(approved=True).count()
        cache.set(cache_key, count, 300)
        return count

    def resolve_tags(self, info):
        return list(self.tags.all().values("id", "name"))
