
import graphene
from graphene_django import DjangoObjectType
from .models import *
from admin_app.models import *
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

class LikesByNewsLoader(DataLoader):
    def batch_load_fn(self, news_ids):
        qs = Like.objects.filter(news_id__in=news_ids).select_related("user")
        news_map = {news_id: [] for news_id in news_ids}
        for like in qs:
            news_map[like.news_id].append(like)
        return Promise.resolve([news_map[nid] for nid in news_ids])
    

class CandidatesByWardLoader(DataLoader):
    def batch_load_fn(self, ward_ids):
        qs = ElectionResult.objects.filter(ward_id__in=ward_ids).only(
            "id", "name", "party", "vote_count", "ward_id"
        )
        ward_map = {wid: [] for wid in ward_ids}
        for candidate in qs:
            ward_map[candidate.ward_id].append(candidate)
        # Return in same order as ward_ids
        return Promise.resolve([ward_map[wid] for wid in ward_ids])




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

class SubCategoryType(DjangoObjectType):
    news = graphene.List(lambda: NewsType, page=graphene.Int(), page_size=graphene.Int())

    class Meta:
        model = SubCategory
        fields = ("id", "name", "slug", "category", "image")

    def resolve_news(self, info, page=1, page_size=10):
        cache_key = f"subcategory_{self.id}_news_page_{page}"
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        qs = self.news.select_related("category", "author").prefetch_related("tags").defer("content").order_by("-publish_date")
        
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated = list(qs[start:end])
        cache.set(cache_key, paginated, CACHE_TIMEOUT)
        return paginated

class CategoryType(DjangoObjectType):
    subcategories = graphene.List(lambda: SubCategoryType, page=graphene.Int(), page_size=graphene.Int())

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "image")

    def resolve_subcategories(self, info, page=1, page_size=10):
        cache_key = f"category_{self.id}_subcategories_page_{page}"
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        qs = list(self.subcategories.all())
        
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated = qs[start:end]
        cache.set(cache_key, paginated, CACHE_TIMEOUT)
        return paginated

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
    likes = graphene.List(LikeType)

    class Meta:
        model = News
        fields = ("id", "title", "slug", "content", "image", "publish_date", "status", "author", "category", "tags", "likes", "comments")

    # ------------------ Resolvers ------------------
    def resolve_comments(self, info):
        return CommentsByNewsLoader(info.context).load(self.id)

    def resolve_likes_count(self, info):
        if hasattr(self, 'likes_count'):
            return self.likes_count
            
        cache_key = f"news_{self.id}_likes_count"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        count = self.likes.count()
        cache.set(cache_key, count, CACHE_TIMEOUT)
        return count

    def resolve_comments_count(self, info):
        if hasattr(self, 'comments_count'):
            return self.comments_count

        cache_key = f"news_{self.id}_comments_count"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        count = self.comments.filter(approved=True).count()
        cache.set(cache_key, count, CACHE_TIMEOUT)
        return count

    def resolve_tags(self, info):
        if hasattr(self, '_prefetched_objects_cache') and 'tags' in self._prefetched_objects_cache:
             return self.tags.all()

        cache_key = f"news_{self.id}_tags"
        cached = cache.get(cache_key)
        if cached:
            return cached
        qs = list(self.tags.all())
        cache.set(cache_key, qs, CACHE_TIMEOUT)
        return qs
    
    def resolve_likes(self, info):
        return LikesByNewsLoader(info.context).load(self.id)
    




class ElectionResultType(DjangoObjectType):
    candidatePhotoUrl = graphene.String()
    partyLogoUrl = graphene.String()

    class Meta:
        model = ElectionResult
        fields = ("id", "name", "party", "vote_count","party_logo", "candidate_photo")  # only necessary fields

    def resolve_candidatePhotoUrl(self, info):
        if self.candidate_photo:
            return info.context.build_absolute_uri(self.candidate_photo.url)
        return None

    def resolve_partyLogoUrl(self, info):
        if self.party_logo:
            return info.context.build_absolute_uri(self.party_logo.url)
        return None


class WardType(DjangoObjectType):
    candidates = graphene.List(ElectionResultType)

    class Meta:
        model = Ward
        fields = ("id", "ward_number", "ward_name", "total_voters", "candidates")

    def resolve_candidates(self, info):
        return list(self.candidates.all())  # convert QuerySet to list




